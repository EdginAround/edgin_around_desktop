# Edgin' Around

*"Edgin' Around'* is a survival game. It draws inspiration from the genre but also beyond from games
like:

 - Don't Starve
 - Civilisation
 - Mobile Legends: Bang Bang

# Installation

The game is in a very early stage of development. By using it you essentially become a part of alpha
testing team. In future we plan to make it available on Steam or Android, but for now it requires a
manual installation. This guide assumes you have a basic knowledge of Linux command-line and
familiarity with tools like `git` or `python`.

### 1. Install dependencies

Install `git`, `python3` and `pip3`.

On Ubuntu it's:
```sh
sudo apt install git python3 pip3
```

On Arch Linux it's:
```sh
sudo pacman -S git python pip
```

### 2. Get source code

```
git clone git@github.com:EdginAround/edgin_around.git
cd edgin_around
```

### 3. Install Python modules

Install Python modules with the following command:
```sh
pip install -r requirement.txt
```

### 4. Get image and sound files

We store image and sound resource files separately from the code. You can download and unpack them
with following commands:
```sh
wget https://github.com/EdginAround/edgin_around_resources/releases/download/0.0.1/edgin_around_resources.zip
unzip edgin_around_resources.zip
```

### 5. Run the game

If everything went right you can run the game with the following command:
```sh
python edgin_around.py
```

