def descriptions():
    return {
    "tf_folder": {
        "description": '/tf folder location',
        "default": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Team Fortress 2\\tf",
        "type": "string"
    },
    "framerate": {
        "description": 'The framerate you would like to record at\n(Stick to standard framerates: 30, 60, 120, 240)',
        "default": 60,
        "type": "integer"
    },
    "crosshair": {
        "description": 'If you would like to enable or disable the crosshair\n1 for enable or 0 for disable',
        "default": 0,
        "type": "boolean"
    },
    "HUD": {
        "description": 'If you would like to enable or disable the HUD\n1 for enable or 0 for disable',
        "default": 1,
        "type": "boolean"
    },
    "text_chat": {
        "description": 'If you would like to enable or disable the text chat\n1 for enable or 0 for disable',
        "default": 0,
        "type": "boolean"
    },
    "voice_chat": {
        "description": 'If you would like to enable or disable the voice chat\n1 for enable or 0 for disable',
        "default": 0,
        "type": "boolean"
    },
    "commands": {
        "description": 'Any additional commands to run before a clips starts to record',
        "default": "",
        "type": "string"
    },
    "end_commands": {
        "description": 'Commands to run once recording is completed. Often used to reset values to the default prefered for play values',
        "default": "",
        "type": "string"
    },
    "method": {
        "description": 'The method of recording that ryukbot will take to record\nh264 uses quicktime to directly get mp4\nLeaving it blank will use tga recording like Lawena by default',
        "default": "h264",
        "type": "string"
    },
    "start_delay": {
        "description": 'The delay at the start of a demo before it starts skipping to the first clip\nCan be helpful to prevent crashes',
        "default": 250,
        "type": "integer"
    },
    "before_bookmark": {
        "description": 'The ticks to record before each bookmark\n1500 ticks is about 10 seconds',
        "default": 1000,
        "type": "integer"
    },
    "after_bookmark": {
        "description": 'The ticks to record after each bookmark\n1500 ticks is about 10 seconds',
        "default": 200,
        "type": "integer"
    },
    "before_killstreak_per_kill": {
        "description": 'The ticks to record per kill in the killstreak\nThis should be equal or a little larger than the time allowed between kills in your game or prec settings\n1500 ticks is about 10 seconds',
        "default": 500,
        "type": "integer"
    },
    "after_killstreak": {
        "description": 'The ticks to record after each killstreak\n1500 ticks is about 10 seconds',
        "default": 300,
        "type": "integer"
    },
    "minimum_ticks_between_clips": {
        "description": 'The amount of ticks between the end of one clip and the start of the next before ryukbot just combines them\n1500 ticks is about 10 seconds',
        "default": 500,
        "type": "integer"
    },
    "interval_for_rewind_double_taps": {
        "description": 'How long between each tap of the button is allowed for it to be counted a double tap\nKeep this number low to prevent accidental double (or more) taps\n1500 ticks is about 10 seconds',
        "default": 200,
        "type": "integer"
    },
    "rewind_amount": {
        "description": 'The amount of ticks to rewind when a double tap happens\n1500 ticks is about 10 seconds',
        "default": 1000,
        "type": "integer"
    },
    "record_continuous": {
        "description": 'Automatically start recording the next demo when the current one is done\nIf disabled it will close tf2 when complete\n1 for enable or 0 for disable',
        "default": 1,
        "type": "boolean"
    },
    "welcome_message": {
        "description": 'Enable or disable the welcome message at the start of the program\n1 for enable or 0 for disable',
        "default": 1,
        "type": "boolean"
    },
    "console_detail": {
        "description": 'The amount of detail to show in the console as the program is running\n0 for none up to 4 to show everything',
        "default": 4,
        "type": "integer"
    },
    "clear_events": {
        "description": 'Clear the _events.txt or KillStreaks.txt file at the end of process\n1 for enable or 0 for disable',
        "default": 1,
        "type": "boolean"
    },
    "advanced_event_maker": {
        "description": 'Add an extra option to the built in _event.txt maker',
        "default": 1,
        "type": "boolean"
    },
    "safe_mode": {
        "description": 'Enabling will prevent you from being able to overwrite previously made VDM files.',
        "default": 0,
        "type": "boolean"
    },
}