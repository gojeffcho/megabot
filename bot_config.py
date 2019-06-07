
current_courses = [ 'cmput-250',
#                     'intd-350',
#                     'intd-450',
#                     'mlcs-499'
                  ]

CONFIG = {}

CONFIG['Prefix'] = ('!')

CONFIG['GameDevRoles']  = [ 'artists', 'directors', 'developers',
                            'musicians', 'producers', 'writers']
CONFIG['CourseRoles']   = [ 'cmput-general', 'gamedev-general' ] + current_courses

CONFIG['AdminRole']     = 'Daddy'
CONFIG['ModRole']       = 'Sugar Babies'
CONFIG['CapRole']       = 'Dunce Cap'
CONFIG['CrapRole']      = '💩💩💩'
CONFIG['NewRole']       = 'new'
CONFIG['ConfirmedRole'] = 'confirmed'

CONFIG['NotificationsChannel']  = 'notifications'
CONFIG['WelcomeChannel']        = 'welcome'
CONFIG['ProfilesChannel']       = 'profiles'
CONFIG['RulesChannel']          = 'rules'
CONFIG['StaffChannel']          = 'staff'
CONFIG['EventChannelPrefix']    = 'event'

CONFIG['StatsCategories'] =   [ 'Administration',
                                'Chat',
                                'Courses',
                                'Community',
                                'Event Channels',
                                'Archived Channels'
                              ]

CONFIG['Dice'] = [2, 4, 6, 8, 10, 12, 20, 100, 1000]

CONFIG['8Ball'] = [
                    "It is certain.",
                    "It is decidedly so.",
                    "Without a doubt.",
                    "Yes - definitely.",
                    "You may rely on it.",
                    "As I see it, yes.",
                    "Most likely.",
                    "Outlook good.",
                    "Yes.",
                    "Signs point to yes.",
                    "Reply hazy, try again.",
                    "Ask again later.",
                    "Better not tell you now.",
                    "Cannot predict now.",
                    "Concentrate and ask again.",
                    "Don't count on it.",
                    "My reply is no.",
                    "My sources say no.",
                    "Outlook not so good.",
                    "Very doubtful."
                  ]

CONFIG['EmotePath'] = 'http://megachannel.jeffcho.com/emotes/'
CONFIG['Emotes'] =  {
                      'brogurt': 'brogurt.png',
                      'david': 'david.png',
                      'divad': 'divad.png',
                      'flosiy': 'flosiy.png',
                      'haay': 'haay.jpg',
                      'lmaoest': 'lmaoest.png',
                      'osiy': 'osiy.png',
                      'questionmark': 'questionmark.png',
                      'what': 'what.png',
                      'yikers': 'yikers.png',
                    }                

CONFIG['DATA']            = {}
CONFIG['DATA']['monitor'] = []
CONFIG['DATAFILE']        = '/home/megabot/megabot/data.pkl'

CONFIG['DatabaseFile']    = 'megabot.db'