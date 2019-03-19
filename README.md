# Py2pdf

Converts Python source code with highlighting to PDF.

To use first install required packages:

```
python3 -m pip install -r requirements.txt --user
```

To use it simple pass to ``py2pdf`` name of python file that you want to convert to PDF. For example, if name of your file is ``mycode.py`` then do

```
python3 py2pdf.py mycode.py
```

This will generate ``mycode.pdf``. If you want different name for generated PDF file you can provide it to the command line after ``mycode.py``.