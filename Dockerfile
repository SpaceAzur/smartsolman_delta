FROM opensuse/leap:15

COPY . /smartsolman/

RUN zypper install -y python3 gcc python3-devel python3-pip sqlite3 zip
RUN pip install -r requirements.txt

WORKDIR /smartsolman/data/dev/SparseMatrixSimilarity/DELTA

# ENTRYPOINT [ "python3" ]
