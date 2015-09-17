# Fixing the CURL bug in Amazon AMI (http://blog.unixy.net/2013/08/curl-77-problem-with-the-ssl-ca-cert-path-access-rights-resolved/)
yum install -y wget
mkdir /usr/src/ca-certificates && cd /usr/src/ca-certificates
wget http://mirror.centos.org/centos/6/os/i386/Packages/ca-certificates-2015.2.4-65.0.1.el6_6.noarch.rpm
rpm2cpio ca-certificates-2015.2.4-65.0.1.el6_6.noarch.rpm | cpio -idmv
cp -pi ./etc/pki/tls/certs/ca-bundle.* /etc/pki/tls/certs/
