from django.utils.translation import gettext_lazy as _
JET_SIDE_MENU_ITEMS = [
    {
        'label': _('Users'),
        'app_label': 'auth',
        'items': [
            {'name': 'user'},
        ]
    },
    {
        'label': _('CSVTasks'),
        'app_label': 'data_processor',
        'items': [
            {'name': 'csvtask'},
        ]
    },
]
JET_CHANGE_FORM_SIBLING_LINKS = False
JET_SIDE_MENU_COMPACT = True
JET_THEMES = [
    {
        'theme': 'default',  # theme folder name
        'color': '#47bac1',  # color of the theme's button in user menu
        'title': 'Default'  # theme title
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]
