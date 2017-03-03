REM
REM due to a couple of bugs in 3.6.0 we have to stay on 3.5 until 3.6.x fixes them
REM
REM Here's one that's already known:
REM https://bugs.python.org/issue29319
REM
REM I also found that I have to manually put this in the beginning of get-pip.py
REM    import site
REM    site.getusersitepackages()
REM otherwise I get an error in: "locations.py, line 88"
REM since site.USER_SITE "Can be None if getusersitepackages() hasn’t been called yet."
REM see: https://docs.python.org/3/library/site.html
REM
venv\scripts\python -m osnap.osnapy -p 3.5.3