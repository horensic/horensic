# horensic
A library for developing digital forensic tools and useful scripts for forensic analysis  
horensic은 포렌식 도구 개발을 위한 라이브러리와 포렌식 분석을 위해 제작한 스크립트입니다.

## Dependencies

* Python 3.6.x

## Installation
    $ python setup.py install

## library
* NTFS (MFT, $I30)
* Output (CSV, SQLite, HTML)
* Predefined regular expression
* Timestamp (Filetime, ...)
* TODO
    * EVTX 
    * Korean

## scripts
* File hashing
* JPG steganography scan
* MFT / $I30 parser
* TODO
    * Raw disk image (.dd, .001) parser
    * RTF plain-text collector
    * E-mail (.eml) parser
    * MBR, VBR check / repair
    * Windows Event Log (EVTX) Parser
