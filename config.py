
current_courses = [ 'cmput-250',
                    'cmput-301',
                    'cmput-302',
                    'intd-350',
                    'intd-450',
                    'mlcs-499'
                  ]

CONFIG = {}

CONFIG['Prefix'] = ('!')

CONFIG['ChannelRoles']  = [ 'artists', 'directors', 'developers',
                            'musicians', 'producers', 'writers']
CONFIG['CourseRoles']   = [ 'cmput-general', 'gamedev-general' ] + current_courses

CONFIG['AdminRole']     = 'Daddy'
CONFIG['ModRole']       = 'Sugar Babies'
CONFIG['NewRole']       = 'new'
CONFIG['ConfirmedRole'] = 'confirmed'

CONFIG['NotificationsChannel']  = 'notifications'
CONFIG['WelcomeChannel']        = 'welcome'
CONFIG['ProfilesChannel']       = 'profiles'
CONFIG['RulesChannel']          = 'rules'
CONFIG['StaffChannel']          = 'staff'