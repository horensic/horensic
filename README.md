# horensic
A library for developing digital forensic tools and useful scripts for forensic analysis  
horensic은 포렌식 도구 개발을 위한 라이브러리이며, 포렌식 분석을 위해 제작한 스크립트들을 포함하고 있습니다.

## Getting Started
horensic is a Python library. It is based on Python 3.6.x. If you only install Python 3.6.x, you can import the necessary modules or use prebuilt scripts.  
horensic은 파이썬 라이브러리입니다. 그리고 Python 3.6.x를 기준으로 작성되었습니다. Python 3가 설치되어 있다면
horensic 라이브러리에서 필요한 모듈을 가져오거나 미리 작성된 스크립트를 사용할 수 있습니다. 

### Prerequisites

* Python 3.6 or later

### Installing

    $ python setup.py install

### Supporting

library:
* EVTX
* NTFS (MFT, $I30)
* Output (CSV, SQLite, HTML)
* Predefined regular expression
* Timestamp (Filetime, ...)
* TODO
    * Korean

scripts:
* File hashing
* JPG steganography scan
* MFT / $I30 parser
* TODO
    * Raw disk image (.dd, .001) parser
    * RTF plain-text collector
    * E-mail (.eml) parser
    * MBR, VBR check / repair
    * Windows Event Log (EVTX) Parser
    

    

