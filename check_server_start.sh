workdir=$(dirname $0)
cd $workdir
echo "workdir: $workdir"
ps -ef |grep check_server.py |grep -v grep |awk '{ print $2}' |xargs kill -9
echo "启动服务..."
nohup python3 check_server.py >nohup.log 2>&1 &
echo "启动服务成功"
sleep 2
ps -ef |grep check_server.py
