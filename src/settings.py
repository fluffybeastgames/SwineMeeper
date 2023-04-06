class SwineStrings:
    def __init__(self, lang):
        self.active_language = lang
        self.constants = self.get_str_consts() 


    def get_string(self, key):
        try:
            val =  self.constants[self.active_language][key]
        except KeyError:
            print('whoops')
            val = 'ERR'        
        
        return val


    def get_str_consts(self, version=0.01):
        # keys are based on ISO 639-1
        dict_out = {}

        dict_out['en'] = { # English (standard)
            'title': 'SwineMeeper',
            'menu_cascade_file': 'File',
            'menu_new_game': 'New Game',
            'menu_about': 'About...',
            'menu_exit': 'Quit',
            'menu_cascade_game': 'Game',
            'menu_settings': 'Game Settings',
            'menu_help': 'Help',
            'menu_toggle_debug': 'Toggle Debug Mode',
            'wind_about_title': 'About SwineMeeper',
            'wind_about_text': 'All About SwineMeeper',
            'wind_settings_title': 'Game Settings',
            'wind_settings_rows': 'Rows',
            'wind_settings_cols': 'Cols',
            'wind_settings_bombs': 'Bombs',
            'wind_settings_apply': 'Apply Settings',
            'wind_settings_cancel': 'Cancel',
            'wind_help_title': 'Help',
            'wind_help_text': 'Here\'s how to play SwineMeeper',
            'prompt_confirm_exit_title': 'Exit',
            'prompt_confirm_exit_msg' : 'Do you want to quit?',
            'menu_cascade_language': 'Language',
            'menu_lang_en': 'English (United States)',
            'menu_lang_fr': 'Français (France)',
            'menu_lang_es': 'Español (Español)',
            'menu_lang_nl': 'Nederlands (Nederland)',
            'difficulty': 'Difficulty',
            'difficulty_easy': 'Easy',
            'difficulty_med': 'Medium',
            'difficulty_hard': 'Hard',
            'difficulty_cust': 'Custom',
            'scoreboard_header': 'High Scores',
            'scoreboard_name': 'Name',
            'scoreboard_score': 'Score',
            'scoreboard_date': 'Date'     
        }

        dict_out['fr'] = { # French (France)
            'title': 'SwineMeeper',
            'menu_cascade_file': 'Fichier',
            'menu_new_game': 'Nouveau',
            'menu_about': 'À propos du SwineMeeper',
            'menu_exit': 'Quitter',
            'menu_cascade_game': 'Jeu',
            'menu_settings': 'Paramètres de Jeu',
            'menu_help': 'Aide',
            'menu_toggle_debug': 'Vue de Débogage',
            'wind_about_title': 'À propos du SwineMeeper',
            'wind_about_text': 'À propos du SwineMeeper',
            'wind_settings_title': 'Paramètres de Jeu',
            'wind_settings_rows': 'Lignes',
            'wind_settings_cols': 'Colonnes',
            'wind_settings_bombs': 'Bombes',
            'wind_settings_apply': 'Appliquer les paramètres',
            'wind_settings_cancel': 'Annuler',
            'wind_help_title': 'Aide',
            'wind_help_text': 'fr___Here\'s how to play SwineMeeper',
            'prompt_confirm_exit_title': 'Quitter?',
            'prompt_confirm_exit_msg' : 'Voulez-vous quitter le programme?',
            'menu_cascade_language': 'Langue',
            'menu_lang_en': 'English (United States)',
            'menu_lang_fr': 'Français (France)',
            'menu_lang_es': 'Español (Español)',
            'menu_lang_nl': 'Nederlands (Nederland)',
            'difficulty': 'Difficulté',
            'difficulty_easy': 'Facile',
            'difficulty_med': 'Moyen',
            'difficulty_hard': 'Difficile',
            'difficulty_cust': 'Coutume',
            'scoreboard_header': 'Scores élevés',
            'scoreboard_name': 'Nom',
            'scoreboard_score': 'Score',
            'scoreboard_date': 'Date'                 
        }

        dict_out['nl'] = { # Dutch (standard)
            'title': 'nl___SwineMeeper',
            'menu_cascade_file': 'nl___File',
            'menu_new_game': 'nl___New Game',
            'menu_about': 'nl___About...',
            'menu_exit': 'nl___Quit',
            'menu_cascade_game': 'nl___Game',
            'menu_settings': 'nl___Settings',
            'menu_help': 'nl___Help',
            'menu_toggle_debug': 'nl___Toggle Debug Mode',
            'wind_about_title': 'nl___About SwineMeeper',
            'wind_about_text': 'nl___All About SwineMeeper',
            'wind_settings_title': 'nl___Game Settings',
            'wind_settings_rows': 'nl___Rows',
            'wind_settings_cols': 'nl___Cols',
            'wind_settings_bombs': 'nl___Bombs',
            'wind_settings_apply': 'nl___Apply Settings',
            'wind_settings_cancel': 'nl___Cancel',
            'wind_help_title': 'nl___Help',
            'wind_help_text': 'nl___Here\'s how to play SwineMeeper',
            'prompt_confirm_exit_title': 'nl___Exit',
            'prompt_confirm_exit_msg' : 'nl___Do you want to quit?',
            'menu_cascade_language': 'nl___Language',
            'menu_lang_en': 'English (United States)',
            'menu_lang_fr': 'Français (France)',
            'menu_lang_es': 'Español (Español)',
            'menu_lang_nl': 'Nederlands (Nederland)',
            'difficulty': 'nl___Easy',
            'difficulty_easy': 'nl___Easy',
            'difficulty_med': 'nl___Medium',
            'difficulty_hard': 'nl___Hard',
            'difficulty_cust': 'nl___Custom',
            'scoreboard_header': 'nl___High Scores',            
            'scoreboard_name': 'nl___Name',
            'scoreboard_score': 'nl___Score',
            'scoreboard_date': 'nl___Date'                     
        }

        dict_out['es'] = { # Spanish (Spain)
            'title': 'fr___SwineMeeper',
            'menu_cascade_file': 'es___File',
            'menu_new_game': 'es___New Game',
            'menu_about': 'es___About...',
            'menu_exit': 'es___Quit',
            'menu_cascade_game': 'es___Game',
            'menu_settings': 'es___Settings',
            'menu_help': 'es___Help',
            'menu_toggle_debug': 'es___Toggle Debug Mode',
            'wind_about_title': 'es___About SwineMeeper',
            'wind_about_text': 'es___All About SwineMeeper',
            'wind_settings_title': 'es___Game Settings',
            'wind_settings_rows': 'es___Rows',
            'wind_settings_cols': 'es___Cols',
            'wind_settings_bombs': 'es___Bombs',
            'wind_settings_apply': 'es___Apply Settings',
            'wind_settings_cancel': 'es___Cancel',
            'wind_help_title': 'es___Help',
            'wind_help_text': 'es___Here\'s how to play SwineMeeper',
            'prompt_confirm_exit_title': 'es___Exit',
            'prompt_confirm_exit_msg' : 'es___Do you want to quit?',
            'menu_cascade_language': 'es___Language',
            'menu_lang_en': 'English (United States)',
            'menu_lang_fr': 'Français (France)',
            'menu_lang_es': 'Español (Español)',
            'menu_lang_nl': 'Nederlands (Nederland)',
            'difficulty': 'es___Easy',
            'difficulty_easy': 'es___Easy',
            'difficulty_med': 'es___Medium',
            'difficulty_hard': 'es___Hard',
            'difficulty_cust': 'es___Custom',
            'scoreboard_header': 'es___High Scores',            
            'scoreboard_name': 'es___Name',
            'scoreboard_score': 'es___Score',
            'scoreboard_date': 'es___Date'                     
        }

        return dict_out


strings = SwineStrings(lang='en')