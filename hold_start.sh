tag=$1
all_tag="5J F9 Y4 6J FR U2 W9 VY VB"

if [ ! -n "$tag" ]
then
  echo "$tag"
  echo "必须传入启动参数"
  echo "支持app [5J,F9,Y4,6J,FR,U2,W9,VY,VB]"
  echo "全部启动 all"
  echo "单个启动 app_name"
  echo "全部结束 kill all"
  echo "结束单个 kill app_name"
  exit
fi


star_app(){
  ps -ef |grep "hold_main.py $1" |grep -v grep |awk '{ print $2}' |xargs kill -9
  echo "准备启动 app $1"
  pid=`nohup python3 hold_main.py $1 >/dev/null 2>&1 &  echo $!`
  echo "app 启动中 pid $pid"
  sleep 3
  ps -ef |grep "$pid" |grep -v grep
  echo "$pid 启动完毕"
}

stop_app(){
  if [ ! -n "$1" ]
  then
    echo "请传入需要结束的app"
    exit 0
  elif [ $1 == "all" ]
  then
    echo "查询全部进程"
    ps -ef |grep "hold_main.py" |grep -v grep
    echo "结束全部进程"
    ps -ef |grep "hold_main.py" |grep -v grep |awk '{ print $2}' |xargs kill -9
    sleep 1
    echo "再次查询全部进程"
    ps -ef |grep "hold_main.py" |grep -v grep
    exit 0
  else
    echo "查询进程"
    ps -ef |grep "hold_main.py $1" |grep -v grep
    echo "结束进程"
    ps -ef |grep "hold_main.py $1" |grep -v grep |awk '{ print $2}' |xargs kill -9
    sleep 1
    echo "再次查询进程"
    ps -ef |grep "hold_main.py $1" |grep -v grep |awk '{ print $2}'
    exit 0
  fi
}

if [ $tag == "all" ]
then
  for i in $all_tag
  do
    star_app $i
  done
elif [ $tag == "kill" ]
then
  stop_app $2
else
  star_app $tag
fi