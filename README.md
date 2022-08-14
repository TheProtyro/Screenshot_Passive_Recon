# Screenshot_Passive_Recon
A tool used to screenshot the passive reconnaissance part of an external or web pentest.

## Dependencies

```
pip3 install -r requirements.txt
```
Then install [geckodriver](https://github.com/mozilla/geckodriver/releases). The executable needs to be in the PATH.

```
root@kali:/opt# mv ~/Downloads/geckodriver-v0.31.0-linux64.tar.gz /opt/geckodriver-v0.31.0-linux64.tar.gz
root@kali:/opt# tar -xvf geckodriver-v0.31.0-linux64.tar.gz
geckodriver
root@kali:/opt# export PATH=$PATH:/opt
```

If you want to permanently set your `$PATH` you need to edit your profile file and insert the `export PATH` line to it. The profile file depends of your shell.

## Usage

```
python3 screenshot_passive_recon.py -d domain.tld
```

## TODO list

- [ ] Output folder
- [ ] More enum / screen -> GitHub, Hunter.io...
- [ ] Reject cookies on netcraft to clean screen
- [ ] Scroll down on netcraft websites to have technologies in use
- [ ] Reduce time needed on the Netcraft part, or add option to skip this part
- [ ] Increase browser / screen size
- [ ] Clean code
- [ ] Other ideas are welcome :)
