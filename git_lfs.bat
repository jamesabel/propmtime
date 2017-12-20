REM
REM https://github.com/git-lfs/git-lfs/wiki/Tutorial
REM
REM this script assumes you have done the following
REM
REM installed git-lfs (see https://github.com/git-lfs/git-lfs/wiki/Installation)
REM git lfs install
REM git lfs track installers\*.exe
REM git add .gitattributes "installers\*.exe"
REM
REM then you can do the updates that upload binaries to git-lfs
git commit -m "Add installers"
git push
