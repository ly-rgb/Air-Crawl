workdir=$(dirname $0)
cd $workdir
echo "workdir: $workdir"
ps -ef |grep pahsell_main.py |grep -v grep |awk '{ print $2}' |xargs kill -9
echo "清理日志..."
rm -rf ./log/*
sleep 2
echo "启动服务..."
nohup python3 pahsell_main.py 0 10241 >/dev/null 2>&1 &
echo "启动服务成功"
sleep 2
ps -ef |grep python3
