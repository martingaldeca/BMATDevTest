import logging
from datetime import datetime
import os
from pathlib import Path

import dask.dataframe as dd
import pandas as pd
from math import ceil

from backend.celery_backend.celery import shared_task

from data_processor.models import CSVTask, CSVTaskFile, CSVTaskFileRelation

env = os.environ
CSVS_PATH = env.get('CSVS_PATH', 'apps/data_processor/csvs/')
COLUMN_NAMES = ['Song', 'Date', 'Number of Plays']
logger = logging.getLogger(__name__)


@shared_task(name='task_process_csv')
def task_process_csv(task_uuid: str):
    csv_task = CSVTask.objects.get(uuid=task_uuid)
    process_csv(task_uuid=task_uuid, csv_path=csv_task.input_file.path)


def _check_format(dataframe: dd.DataFrame) -> dd.DataFrame:
    """
    :param dataframe:
    :return:
    """
    columns_names = dataframe.columns.tolist()
    if columns_names != COLUMN_NAMES:
        # Check if the types are valid and the csv has not headers
        try:
            # Check if the format are ok
            datetime.strptime(columns_names[1], '%Y-%m-%d')
            plays = int(columns_names[2])

            # Rename the dataframe columns
            dataframe = dataframe.rename(
                columns={
                    columns_names[i]: COLUMN_NAMES[i] for i in range(len(COLUMN_NAMES))
                },
            )

            # Add to the dataframe
            df = pd.DataFrame.from_dict(
                {
                    COLUMN_NAMES[0]: [columns_names[0], ],
                    COLUMN_NAMES[1]: [columns_names[1], ],
                    COLUMN_NAMES[2]: [plays, ],
                }
            )
            dataframe = dd.concat([dataframe, df])
        except Exception:
            raise ValueError('not valid headers')

    try:
        # Coerce and then remove nan if you want to use that rows
        dataframe[COLUMN_NAMES[2]] = dd.to_numeric(dataframe[COLUMN_NAMES[2]])

        # This index will take few extra seconds but will order our output file very well
        dataframe = dataframe.set_index('Date', sorted=True)
    except ValueError as ex:
        raise TypeError(f'Number of Plays must be of type int. The file is corrupted. {str(ex)}')

    return dataframe


def process_csv(task_uuid: str, csv_path: str):
    """
    In order to test better this for the first part of the test I separate it in a different function
    """

    start = datetime.now()

    # Get the associated task
    csv_task = CSVTask.objects.get(uuid=task_uuid)
    logger.info(f'Processing file {csv_path} for task {task_uuid}')

    # Process the file using dask and check the format
    df = dd.read_csv(csv_path)
    try:
        output_dataframe = _check_format(df)
    except Exception as ex:
        logger.exception(
            'Problem processing task',
            extra={
                'task_uuid': csv_task.uuid.hex,
                'ex': ex
            }
        )
        csv_task.error_processing = True
        csv_task.error_message = str(ex)
        csv_task.save()
        raise ex

    # In order to avoid only 1 partition if file is huge we will assume that each MAX_SINGLE_FILE_SIZE gb of the initial
    # file should have 1 partition
    # By default 500MB it depends on the files and also on the server that will run the code
    max_single_file_size = int(env.get('MAX_SINGLE_FILE_SIZE', 500_000_000))
    split_out = ceil(os.path.getsize(csv_path) / max_single_file_size)  # Ceil just in case is only 1 partition needed
    logger.info(f'Will group by the output file in {split_out} files')

    # The main operation of the problem is quite simple, just group by song and day and sum the third column
    # Sort to False in order of avoid future problems
    output_dataframe = output_dataframe.groupby(['Song', 'Date'], sort=False).sum(split_out=split_out)
    output_dataframe = output_dataframe.reset_index()
    output_dataframe.to_csv(f'{CSVS_PATH}out/{task_uuid}-*.csv', index=False)

    # Associate the files to the task. All files will move to the media path where can be reached with the api
    for file in Path(f'{CSVS_PATH}/out/').glob(f'{task_uuid}-*.csv'):
        os.system(f'mv {file.as_posix()} /src/media/{file.name}')
        csv_task_file = CSVTaskFile.objects.create()
        csv_task_file.output_file.name = file.name
        csv_task_file.save()
        CSVTaskFileRelation.objects.create(csv_task=csv_task, csv_task_file=csv_task_file)
    logger.info(f'Process for {task_uuid} ends in {datetime.now() - start}')
