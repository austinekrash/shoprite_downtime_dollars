# Shoprite_downtime_dollars_bot!
 Automatically completes offers to earn shoprite dollars, written in Python! :raised_hands: 

<h2>Overview</h2>

Headless selenium bot to click through offers so you don't have to. Tested working on Digital Ocean.

<h2>Features</h2> 

- Detects all offers, completes open offers and skips completed ones.
- Optional headless mode
- Logs offer results


<h2>REQUIREMENTS</h2>

- Python 3.6
- Selenium 3.14.0
- Geckodriver for Selenium 

<h2>HOW TO USE</h2> 

1. Clone and navigate to repo
2. Modify ms_rewards_login_dict.json with your account names and passwords, remove .example from filename.
3. Enter into cmd/terminal/shell: `pip install -r requirements.txt`
	- This installs dependencies (selenium)
4. Install geckodriver.
	- download [geckodriver here](https://github.com/mozilla/geckodriver)
	- extract to python parent directory e.g. 'C:\Python37-22'
	- ensure geckodriver is added to PATH
5. Enter into cmd/terminal/shell: `python shoprite_downtime_dollars.py --headless`
	- enter `-h` or `--help` for more instructions
		- `--headless` is for headless mode

<h2>TO DO</h2>

- Rewrite script into class-based code or organize monolithic code into different py files for maintainability
- Remove sleeps and replace with micro-sleeps so explicit waits work properly after the page redirects

<h2>License</h2>

100% free to use and open source.  :see_no_evil: :hear_no_evil: :speak_no_evil:


<h2>Versions</h2>

**2018.01**
	- Initial Release!