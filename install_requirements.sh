ret=`python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'`
if [ $ret -eq 2.5 ]; then
    pip install -r requirements-py25.txt --use-mirrors
else 
    pip install -r requirements.txt --use-mirrors
fi
