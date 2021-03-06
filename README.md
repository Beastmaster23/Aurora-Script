[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/Beastmaster23/)
[![Hackage-Deps](https://img.shields.io/hackage-deps/v/schedule?label=schedule)](https://github.com/Beastmaster23/)
[![Hackage-Deps](https://img.shields.io/hackage-deps/v/progress?label=progress)](https://github.com/Beastmaster23/)
# Aurora Scripts

This program will backup files on a weekly at a certain day and time.


## Authors

- [@Beastmaster23](https://github.com/Beastmaster23)


## Demo

![Terminal demo](https://github.com/Beastmaster23/Aurora-Script/blob/master/terminal.gif)


## Features

- Schedule backups for weekly transfers
- Configure script with the class or ini file
- Logs the transfers


## Installation

Install Aurora script

```bash
  pip install schedule progress
  python start.py
```
    
## Run Locally

Clone the project

```bash
  git clone https://github.com/Beastmaster23/Aurora-Script.git
```

Go to the project directory

```bash
  cd Aurora-Script
```

Install dependencies

```bash
  pip install schedule progress
```

Start the backup App

```bash
  python start.py
```


## Usage/Examples

```Python
    from backup_tasker import BackupTasker

    tasker=BackupTasker(["C:\\Users\\user\\Downloads", "C:\\Users\\user\\Desktop"], ["C:\\Users\\user\\backup"], 0)
    tasker.load_config('backup.ini')
    # Schedule the backup easy :)
    tasker.schedule_backup()
```


## Support

For support, email edn1211@gmail.com.


## License

[MIT](https://choosealicense.com/licenses/mit/)

