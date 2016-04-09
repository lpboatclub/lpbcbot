Building for AWS Lambda

1. deploy an EC2 micro instance of Amazon Linux (yum-flavored)
2. install the following dependencies
	
	sudo yum groupinstall -y development
    sudo yum install -y git gcc libxml2 libxml2-devel libxslt libxslt-devel python-devel sudo easy_install lxml

3. Download lpbcbot project

    git clone https://github.com/mikeblum/lpbcbot.git

4. Configure virtualenv

    virtualenv env
    source env/bin/activate

5. Pull down Python libraries

	pip install -r ./requirements.txt

