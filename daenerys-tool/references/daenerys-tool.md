# Daenerys Tool Doc (Extract)

基础框架介绍
环境准备
名词术语
Golang 环境准备
Python 环境准备
Hello World
代码生成工具
应用构建
构建之前
inkedep
pip
开发服务
Golang HTTP Server
Golang HTTP Client
Golang RPC Server
Golang RPC Client
Logging 日志
Metric 统计
便捷 Client
KafkaClient
RedisClient
MySqlClient
ESClient
熔断限流
Trace 功能
配置中心
服务发现功能
框架原理
代码生成工具
本章节介绍项目代码模板生成工具的使用方式。利用工具可以快速构建服务，使同学们只专注于业务开发。同时也避免新建项目采用代码拷贝方式带来一些不必要的问题，影响开发效率。
安装前准备
代码自动生成工具的安装是依赖基础库的。与安装其他三方依赖库类似，您需要提前安装 Golang 并配置好 Golang 的开发环境。同时需要保证基础库代码是最新的。下面是一些 Checklist，请确认本地环境。
首先需要安装
Go
(
version 1.17+ is required
)
依赖包管理工具
inkedep
配置好 GOPATH 路径，GOPATH 的介绍可以参考文档
GOPATH
基础库代码保持最新。
基础库代码更新步骤如下，请注意 GOPATH 的正确性。
由于代码生成工具的安装依赖基础库 daenerys 库, 下面我们来下载 daenerys 库，使用 master 最新版本即可。
如果本地没有基础库 daenerys 包，那么可以通过 inkedep get 下载。
$ inkedep get git.inke.cn/inkelogic/daenerys
如果没有 inkedep 工具，要使用 go get 来下载的话，请注意存放路径为 $GOPATH/src/git.inke.cn/inkelogic
代码生成工具同时也依赖与更新基础库的 golang 库, 使用
master
最新版本即可。
如果本地没有基础库 golang 包，那么可以通过 inkedep get 或者 go get 下载。
$ inkedep get git.inke.cn/BackendPlatform/golang
如果没有 inkedep 工具，要使用 go get 来下载的话，请注意存放路径为 $GOPATH/src/git.inke.cn/BackendPlatform
开始安装
下载代码生成工具包, 使用 master 分支最新代码。
# 用inkedep get 下载最新的master包
$ inkedep get git.inke.cn/BackendPlatform/daenerys-tool
# 安装daenerys工具
$ cd $GOPATH/src/git.inke.cn/BackendPlatform/daenerys-tool/daenerys
$ go install
# [可选]安装dae工具：为daenerys工具的快捷方式
$ cd $GOPATH/src/git.inke.cn/BackendPlatform/daenerys-tool/dae
$ go install
# 查看是否安装成功,一般安装到$GOPATH/bin下
$ ls -l $GOPATH/bin/daenerys
-rwxr-xr-x  1 golang  staff  15713484  6 12  2020 /Users/golang/go/bin/daenerys
如果安装成功，则可以直接运行 daenerys 命令查看一些提示信息。如果提示没找到命令，那么需要检查下 GOPATH 是否成功添加到系统环境变量 PATH 中。
$ daenerys
Your tools version is latest, skip self update.
Generate Usability Code, which base on INKE Daenerys Framework.
Usage:
daenerys [flags]
daenerys [command]
Available Commands:
help        Help about any command
new         Create a new Daenerys project.
tool        Daenerys is a very fast static site generator
update      update daenerys tool.
version     Print the version number of daenerys tool
Flags:
-h, --help   help for daenerys
Use "daenerys [command] --help" for more information about a command.
⚠️⚠️⚠️ 注意：部分同学在安装过程中可能遇到找不到 proto 文件的错误。那么需要更新 protoc 工具,建议使用
3.6.1
以上版本。
# macos 安装方式
$ brew install protobuf
$ protoc --version
libprotoc 3.6.1
生成一个 HTTP Server 服务
在开始生成项目之前，请确认代码生成工具是否安装成功。
运行下面的命令来生成一个 HTTP Server 项目。
$ daenerys new --type http <项目名>
或者（快捷方式）：
$ dae new <项目名>
命令执行完成后，会在当前路径下生成一个项目名的目录，例如：demo。
进入到 demo/app 下，执行 go build 编译该项目，编译成功后会在当前路径下生成可执行文件。直接运行改文件即可启动服务。toml 配置文件中配置了服务的监听端口为 10000。待服务启动后，直接通过 curl 命令或者浏览器访问即可。
$ cd demo/app
$ go build
$ ./app --config ./config/ali-test/config.toml
使用 curl 命令访问服务, 来测试服务是否运行正常。
$ curl 'http://localhost:10000/ping'
{
"dm_error": 0,
"error_msg": "0",
"data": {
"result": "ok"
}
}
$
HTTP Server 目录结构介绍
以下为 http server 服务的整体目录结构：
├── README.md
├── api
│   └── demo
│       └── demo.proto // proto文件
├── app
│   ├── build.sh // 编译脚本,发布系统使用
│   ├── config
│   │   └── ali-test
│   │       └── config.toml // 服务的配置文件
│   └── main.go // main入口
├── conf
│   └── config.go // 服务自身的配置结构
├── dao
│   └── dao.go // DB相关
├── manager
│   └── manager.go // 一些外部接口的封装:rpc client, http client, 中间件等
├── model
│   └── model.go // 业务数据结构模型
├── server
│   └── http
│       ├── handler.go // 可以将路由的处理逻辑都放在这里,或根据需要写到与handler同级的单独文件中
│       └── http.go // http服务, 在此处注册路由信息，pb方式会自动注册，默认会注册ping路由
└── service
└── service.go // 具体业务逻辑实现
api 子目录
一般存放服务对外暴露的 API 接口信息，比如 proto 文件，描述 API 信息；code 文件，服务对外暴露的错误码集合。
# 查看api子目录结构
$ tree api
api
├── code
│   └── code.go
└── doc.md
2 directories, 2 files
上面 code.go 的内容如下：
// code.go
package code
import "git.inke.cn/BackendPlatform/golang/ecode"
var (
InvalidParam      = ecode.New(10000)
)
func init() {
ecode.Register(map[int]string{
10000: "XXX错误",
})
}
app 子目录
服务 main.go 入口文件存放在该目录下，该目录还包含
部署系统
编译脚本 build.sh，服务运行的配置文件存放在 app/config/下。
# 查看app子目录结构
$ tree app
app
├── build.sh
├── config
│   └── ali-test
│       └── config.toml
└── main.go
3 directories, 3 files
build.sh 文件是跟服务部署发布相关的，在服务发布过程中，部署系统的执行流程中会找到 build.sh 文件，以执行服务的编译，并且将服务依赖的资源拷贝到目标节点上。
build.sh
#!/bin/bash
# build.sh
cluster_name=$(echo "$1" | sed -r 's/^cop\.([^_\.]+)?_owt\.([^_\.]+)?_pdl\.([^_\.]+)?_cluster\.([^_\.]+)?.*/\4/')
servicegroup_name=$(echo "$1" | sed -r 's/^cop\.([^_\.]+)?_owt\.([^_\.]+)?_pdl\.([^_\.]+)?(.*)?_servicegroup\.([^_\.]+)?.*/\5/')
service_name=$(echo "$1" | sed -r 's/^cop\.([^_\.]+)?_owt\.([^_\.]+)?_pdl\.([^_\.]+)?(.*)?_service\.([^_\.]+)?.*/\5/')
job_name=$(echo "$1" | sed -r 's/^cop\.([^_\.]+)?_owt\.([^_\.]+)?_pdl\.([^_\.]+)?(.*)?_job\.([^_\.]+)?.*/\5/')
#binary name
target=$2
default_target=service
#cluster name
cluster=${cluster_name##*.}
#project path
project_path=$(cd $(dirname $0); pwd)
#src path
src_path=${project_path}
#release path
release_path=release
#bin path
release_bin_path=${release_path}/bin/
#config path
release_config_path=${release_path}/config/
if [ -d "src" ]; then
printf "find src directory，use src directory \n"
src_path=${project_path}/src
fi
if [ -d "app" ]; then
printf "find app directory，use app directory \n"
src_path=${project_path}
fi
if [ ! $target ]; then
target=${default_target}
printf "target is null,use default target name,%s \n" $target
fi
printEnv(){
printf "Print Env \n"
printf "============================================\n"
printf "Commond Params        | %s %s \n" $1  $2
printf "Project Path          | %s\n" $project_path
printf "Src Path              | %s\n" $src_path
printf "Target                | %s\n" $target
printf "Service Nmae          | %s\n" $service_name
printf "Cluster Name          | %s\n" $cluster_name
printf "Cluster 			  | %s\n" $cluster
printf "Job Name              | %s\n" $job_name
printf "Service Group Name    | %s\n" $servicegroup_name
printf "Release Path          | %s\n" $release_path
printf "Release Bin  Path     | %s\n" $release_bin_path
printf "Release Config Path   | %s\n" $release_config_path
printf "============================================\n\n\n"
}
cleanDir(){
printf "Clean Release Dir \n"
printf "============================================\n"
cd $project_path
rm -rf $release_path
if [ $? != 0 ]; then
printf "Clean release dir failed\n"
exit 101
else
printf "Clean release dir successed\n"
fi
mkdir -p $release_config_path
mkdir -p $release_bin_path
printf "============================================\n\n\n"
}
buildBin(){
printf "Build Bin \n"
printf "============================================\n"
cd $src_path
printf "Pull dependence  ...\n"
inkedep build
if [ $? != 0 ]; then
printf "Compiling project failed\n"
exit 100
fi
printf "Pull dependence End\n"
printf "Compiling project ...\n"
go build -o $project_path/release/bin/$target
if [ $? != 0 ]; then
printf "Compiling project failed\n"
exit 102
else
printf "Compiling project successed\n"
fi
cd $project_path
printf "============================================\n\n\n"
}
copyConf(){
printf "Copy Conf Files\n"
printf "============================================\n"
cd $project_path
cp -r config/$cluster/* release/config/
echo "Copying config/$cluster into release/config"
if [ $? != 0 ]; then
printf "Copying conf failed\n"
exit 103
fi
printf "============================================\n\n\n"
}
printRelease(){
printf "Print Release Directory\n"
printf "============================================\n"
cd $project_path
find $release_path
printf "============================================\n\n\n"
}
printEnv
cleanDir
buildBin
copyConf
printRelease
exit 0
}
main.go 文件是整个服务的入口文件，主要逻辑是解析配置，调用该各个资源的初始化函数，最后阻塞并监听信号，等待服务中断推出后，释放相关资源。
// main.go
package main
import (
"flag"
"log"
"os"
"os/signal"
"syscall"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/conf"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/server/http"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/service"
"git.inke.cn/BackendPlatform/golang/logging"
"git.inke.cn/inkelogic/daenerys"
)
func init() {
configS := flag.String("config", "config/config.toml", "Configuration file")
appS := flag.String("app", "", "App dir")
flag.Parse()
daenerys.Init(
daenerys.ConfigPath(*configS),
)
if *appS != "" {
daenerys.InitNamespace(*appS)
}
}
func main() {
defer daenerys.Shutdown()
// init local config
cfg, err := conf.Init()
if err != nil {
logging.Fatalf("service config init error %s", err)
}
// create a service instance
srv := service.New(cfg)
// init and start http server
http.Init(srv, cfg)
defer http.Shutdown()
sigChan := make(chan os.Signal, 1)
signal.Notify(sigChan, syscall.SIGHUP, syscall.SIGQUIT, syscall.SIGTERM, syscall.SIGINT)
for {
s := <-sigChan
log.Printf("get a signal %s\n", s.String())
switch s {
case syscall.SIGQUIT, syscall.SIGTERM, syscall.SIGINT:
log.Println("ccc server exit now...")
return
case syscall.SIGHUP:
default:
}
}
}
服务运行时所需的配置文件，一般放在 app/config 子目录下。我们约定，不同的资源集群使用不同的子目录管理配置文件。比例 ali-test 集群，那么就放在 app/config/ali-test/config.toml 中。关于配置文件中各个参数的说明，请见基础库
daenerys 框架配置文件
章节。
# app/config/ali-test/config.toml
[server]
service_name="ccc"
port = 10000
[log]
level="debug"
logpath="logs"
rotate="hour"
[[server_client]]
service_name="a.b.c"
proto="http"
endpoints="127.0.0.1:8102"
balancetype="roundrobin"
read_timeout=30000
retry_times=1
slow_time = 1000
endpoints_from="consul"
#逗号表示优先调用同机房的
dc=",ali-vpc"
lb_subset_selectors=[["dc"]]
conf 子目录
一般与服务配置文件有关，主要定义了一些数据结构，用于解析配置文件内容。
如下示例，定义了一个 Config 结构体，当前没有定义其他字段。可以根据情况增加相应的字段，来与配置文件中的内容对应。
$ tree conf
conf
└── config.go
1 directory, 1 file
// config.go
package conf
import (
"git.inke.cn/inkelogic/daenerys"
)
type Config struct {
}
func Init() (*Config, error) {
// parse Config from config file
cfg := &Config{}
err := daenerys.ConfigInstance().Scan(cfg)
return cfg, err
}
dao 子目录
该目录下主要存放与 DB/缓存以及其他存储类资源相关的实现逻辑。比如：mysql/redis/es/s3 等等。可以根据实际情况，在 dao 子目录下再细分其他子目录，以便于管理。
$ tree dao
dao
└── dao.go
1 directory, 1 file
如下示例代码，可以在 New()函数中增加其他 dao 实例。示例中还定了两个方法 Ping()和 Close()，Ping()主要用于探测对应的资源是否还可用，Close()主要用于释放相关资源。
// dao.go
package dao
import (
"context"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/conf"
)
// Dao represents data access object
type Dao struct {
c *conf.Config
}
func New(c *conf.Config) *Dao {
return &Dao{
c: c,
}
}
// Ping check db resource status
func (d *Dao) Ping(ctx context.Context) error {
return nil
}
// Close release resource
func (d *Dao) Close() error {
return nil
}
manager 子目录
一般用于存放一些 client 类或对象池等实例的管理。比如 http client， rpc client，kafka client，其他中间件类的 client 实例等等。
$ tree manager
manager
└── manager.go
1 directory, 1 file
以下 manager 示例中，包含了一个 http client，用于调用服务 a.b.c。
// manager.go
package manager
import (
"bytes"
"context"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/conf"
"git.inke.cn/BackendPlatform/golang/logging"
"git.inke.cn/inkelogic/daenerys/http/client"
"git.inke.cn/inkelogic/daenerys/proxy"
"git.inke.cn/tpc/inf/go-upstream/upstream"
)
// Manager represents middleware component
// such as, kafka, http client or rpc client, etc.
type Manager struct {
c           *conf.Config
storeClient *proxy.HTTP
}
func New(conf *conf.Config) *Manager {
return &Manager{
c:           conf,
storeClient: proxy.InitHTTP("a.b.c"),
}
}
func (m *Manager) Ping(ctx context.Context) error {
ctx = upstream.InjectSubsetCarrier(ctx, []string{"dc", "ali-vpc"})
req := client.NewRequest(ctx).
WithMethod("post").
WithPath("/ping").
WithBody(bytes.NewBuffer([]byte(`hello world`)))
rsp, err := m.storeClient.Call(ctx, req)
logging.Infof("resp:%+v, err:%+v", rsp, err)
return nil
}
func (m *Manager) Close() error {
return nil
}
model 子目录：与 conf 子目录的作用有点类似，该目录下主要存放服务业务逻辑相关的数据结构，实现数据与业务逻辑隔离的目的。同样，可以根据服务特性来细化管理 model 数据结构。
$ tree model
model
└── model.go
1 directory, 1 file
该示例定义了个结构体 Model，里面未包含任何字段。可以根据需求定义字段，比如是个用户信息服务，那么可以定一个 UserInfo 的 struct，并包含，Name, Age, Address 等字段。
// model.go
//Generated by the daenerys tool.  DO NOT EDIT!
package model
type Model struct {
}
server 子目录
该子目录下一般会有 http 子目录或 rpc 子目录，用于标识该服务是一个 http 服务，还是 rpc 服务。以 http 服务为例，在 http 子目录下，会有个 http.go，里面主要包含了，http server 的一些入口代码，以及对应的 HTTP 路由注册代码。若服务的路由比较复杂，为了方便管理，可以在同级目录下，新建一个 handle.go，用于专门上线路由注册相关的逻辑。
以下是一个简单的示例：
目录结构如下：
// 查看server子目录结构
$ tree server
server
└── http
├── handler.go
├── http.go
└── router.go
2 directories, 3 files
// http.go
// 其中initRoute(httpServer)包含了所有的HTTP路由注册情况
// 为了方便管理，initRoute(httpServer)的实现在同级目录下的route.go中。
package http
import (
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/conf"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/service"
"git.inke.cn/BackendPlatform/golang/logging"
"git.inke.cn/inkelogic/daenerys"
httpserver "git.inke.cn/inkelogic/daenerys/http/server"
httpplugin "git.inke.cn/inkelogic/daenerys/plugins/http"
)
var (
svc *service.Service
httpServer httpserver.Server
)
// Init create a rpc server and run it
func Init(s *service.Service, conf *conf.Config) {
svc = s
// new http server
httpServer = daenerys.HTTPServer()
// add namespace plugin
httpServer.Use(httpplugin.Namespace)
// register handler with http route
initRoute(httpServer)
// start a http server
go func() {
if err := httpServer.Run(); err != nil {
logging.Fatalf("http server start failed, err %v", err)
}
}()
}
func Shutdown() {
if httpServer != nil {
httpServer.Stop()
}
if svc != nil {
svc.Close()
}
}
http 路由注册信息，该文件中包含了两个 HTTP 接口，其中**/test** 接口的 handler 逻辑比较简单，可以直接写在 initRoute 中。但是当对应的 hangler 逻辑比较复杂时，则可以将其单独存放在独立的文件中。如：handler.go。
// router.go
// Generated by the daenerys tool.  DO NOT EDIT!
package http
import (
httpserver "git.inke.cn/inkelogic/daenerys/http/server"
)
func initRoute(s httpserver.Server) {
s.ANY("/ping", ping)
s.ANY("/test", func(c *httpserver.Context) {
oldData := map[string]string{"hello": "world"}
c.Next()
for k, v := range c.Keys {
oldData[k] = v.(string)
}
c.JSON(oldData, nil)
},
// 增加信息
func(c *httpserver.Context) {
c.Set("aaa", "bbb")
})
}
http handler 逻辑单独放在 handler.go 中管理。此处，只是为了演示说明，
/ping
接口实际逻辑很简单，只是返回了固定的结果。
// handler.go
package http
import (
httpserver "git.inke.cn/inkelogic/daenerys/http/server"
)
func ping(c *httpserver.Context) {
if err := svc.Ping(c.Ctx); err != nil {
c.JSONAbort(nil, err)
return
}
okMsg := map[string]string{"result": "ok"}
c.JSON(okMsg, nil)
}
service 子目录
service 子目录主要包含核心的业务处理逻辑，该部分代码将会整合上面 dao,conf,manager,model 子目录中的代码片段或函数，使得服务功能得以实现。可以根据情况，拆分 service 的实现逻辑，使得业务逻辑代码结构更清晰，更易于维护和开发。
service
└── service.go
1 directory, 1 file
通过以下代码示例可以看到，里面包含了 dao，manager 信息。service.go 中定义了一个 Ping()方法，用于实现特定的业务逻辑。
// service.go
package service
import (
"context"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/conf"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/dao"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/ccc/manager"
)
type Service struct {
c *conf.Config
// dao: db handler
dao *dao.Dao
// manager: other client(s), other middleware(s)
mgr *manager.Manager
}
func New(c *conf.Config) *Service {
return &Service{
c:   c,
dao: dao.New(c),
mgr: manager.New(c),
}
}
// Ping check service's resource status
func (s *Service) Ping(ctx context.Context) error {
s.mgr.Ping(ctx)
return s.dao.Ping(ctx)
}
// Close close the resource
func (s *Service) Close() {
if s.dao != nil {
s.dao.Close()
}
if s.mgr != nil {
s.mgr.Close()
}
}
服务启动后生成的一些日志文件说明:
详细日志介绍请见：
日志
logs 服务日志目录:
balance 日志:服务发现相关日志
gen 日志:框架日志
stat 日志:统计日志，告警监控相关
business 日志:该服务作为 client 请求其他模块的日志
access 日志:该服务作为 server,其他模块请求该服务的日志
debug/info/error 日志:业务逻辑日志
stdout/stderr 日志:其他日志或崩溃日志
crash 日志:服务崩溃日志
生成一个 RPC Server 服务
运行下面的命令来生成一个 RPC 项目，会在当前运行路径下生成。其中 xxx.proto 存放路径建议也放在$GOPATH 下的某个目录下。
$ dae new --type rpc --proto xxx.proto yyy
示例：xxx.proto
syntax = "proto2";
package xxx;
// http 请求将会解析到改结构中
message GetMessageRequest {
optional string message_id = 1; // mapped to the URL
// optional SubMessage sub = 2; // `sub.subfield` is url-mapped
required string name = 3;
}
message SubMessage {
optional string subfield = 1;
}
message Message {
optional string text = 1; // content of the resource
}
service Messaging {
rpc GetMessage (GetMessageRequest) returns (Message);
}
编译并运行服务，查看启动日志的最后两行可以知道 rpc 服务会起两个端口 10000 和 10001。此处启动两个 server 是为了服务能够同时支持 http 协议和 rpc 协议。其中 http 服务的端口号是 rpc 服务的端口号+1。
$ cd yyy/app
$ go build
$ ./app --config ./config/ali-test/config.toml
2024-10-28 16:41:39.712 daenerys/init.go:64 WARN consul backend init error Get "http://127.0.0.1:8500/v1/agent/self?wait=60000ms": dial tcp 127.0.0.1:8500: connect: connection refused
2024-10-28 16:41:39.712 daenerys/init.go:64 INFO consul: Connecting to "127.0.0.1:8500" in datacenter ""
2024-10-28 16:41:39.714 daenerys/daenerys.go:118 WARN consul: Error read service tags, path /service_config/yyy/yyy/service_tags, error Get "http://127.0.0.1:8500/v1/kv/service_config/yyy/yyy/service_tags/192.168.32.15/10000?consistent=&wait=60000ms": dial tcp 127.0.0.1:8500: connect: connection refused
2024-10-28 16:41:39.712639 init daenerys success app: name:yyy namespace: config:./config/ali-test/config.toml
2024/10/28 16:41:39 yyy start
start rpc server on 0.0.0.0:10000
start rpc-http server on 0.0.0.0:10001
此处为了简单期间，以访问 http 接口为例，用 curl 命令来访问 rpc 服务的 http 接口：
# 用http方式访问
rpc的http接口是proto文件中定义的，格式为：package/service/func。
因此上面proto协议定义的http接口为：/xxx/Messaging/GetMessage
$ curl http://localhost:10001/xxx/Messaging/GetMessage
{"text":"id:,name: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}%
RPC Server 目录结构介绍
以下为 rpc server 服务的整体目录结构；可以看到跟 http server 的目录结构基本一样，不同的是 api 子目录中增加的 xxx.proto 相关的文件；以及 server 子目录下是 rpc 子目录和 rpc.go 文件。
├── README.md
├── api
│   ├── code
│   │   └── code.go
│   └── xxx
│       ├── xxx.pb.go
│       └── xxx.proto
├── app
│   ├── build.sh
│   ├── config
│   │   └── ali-test
│   │       └── config.toml
│   ├── main.go
├── conf
│   └── config.go
├── dao
│   └── dao.go
├── manager
│   └── manager.go
├── model
│   └── model.go
├── server
│   └── rpc
│       └── rpc.go
└── service
└── service.go
由于大部分结构和内容都是一致的，因此以下主要介绍不同的地方。
api 子目录
api
├── code
│   └── code.go
└── xxx
├── xxx.pb.go
└── xxx.proto
3 directories, 3 files
在通过代码生成工具 dae 生成代码后，会在 api 子目录下增加一个跟 proto 文件名一样的子目录 xxx(xxx.proto)。其中 xxx/xxx.proto 就是原来的 xxx.proto，代码生成工具只是原样拷贝过来，作为备份使用。另外一个 xxx.pb.go 是通过 protoc 生成的，protoc 会根据 dae 工具指定的方式来绑定生成。详细请见
protoc-gen-daenerys
xxx.pb.go
// rpc server api/xxx/xxx.pb.go
// Code generated by protoc-gen-go. DO NOT EDIT.
// source: xxx.proto
package xxx
import (
fmt "fmt"
math "math"
proto "github.com/golang/protobuf/proto"
proxy "git.inke.cn/inkelogic/daenerys/proxy"
client "git.inke.cn/inkelogic/daenerys/rpc/client"
server "git.inke.cn/inkelogic/daenerys/rpc/server"
context "golang.org/x/net/context"
)
// Reference imports to suppress errors if they are not otherwise used.
var _ = proto.Marshal
var _ = fmt.Errorf
var _ = math.Inf
// This is a compile-time assertion to ensure that this generated file
// is compatible with the proto package it is being compiled against.
// A compilation error at this line likely means your copy of the
// proto package needs to be updated.
const _ = proto.ProtoPackageIsVersion3 // please upgrade the proto package
// http 请求将会解析到改结构中
type GetMessageRequest struct {
MessageId *string `protobuf:"bytes,1,opt,name=message_id,json=messageId" json:"message_id,omitempty"`
// optional SubMessage sub = 2; // `sub.subfield` is url-mapped
Name                 *string  `protobuf:"bytes,3,req,name=name" json:"name,omitempty"`
XXX_NoUnkeyedLiteral struct{} `json:"-"`
XXX_unrecognized     []byte   `json:"-"`
XXX_sizecache        int32    `json:"-"`
}
func (m *GetMessageRequest) Reset()         { *m = GetMessageRequest{} }
func (m *GetMessageRequest) String() string { return proto.CompactTextString(m) }
func (*GetMessageRequest) ProtoMessage()    {}
func (*GetMessageRequest) Descriptor() ([]byte, []int) {
return fileDescriptor_16118676337827bb, []int{0}
}
func (m *GetMessageRequest) XXX_Unmarshal(b []byte) error {
return xxx_messageInfo_GetMessageRequest.Unmarshal(m, b)
}
func (m *GetMessageRequest) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
return xxx_messageInfo_GetMessageRequest.Marshal(b, m, deterministic)
}
func (m *GetMessageRequest) XXX_Merge(src proto.Message) {
xxx_messageInfo_GetMessageRequest.Merge(m, src)
}
func (m *GetMessageRequest) XXX_Size() int {
return xxx_messageInfo_GetMessageRequest.Size(m)
}
func (m *GetMessageRequest) XXX_DiscardUnknown() {
xxx_messageInfo_GetMessageRequest.DiscardUnknown(m)
}
var xxx_messageInfo_GetMessageRequest proto.InternalMessageInfo
func (m *GetMessageRequest) GetMessageId() string {
if m != nil && m.MessageId != nil {
return *m.MessageId
}
return ""
}
func (m *GetMessageRequest) GetName() string {
if m != nil && m.Name != nil {
return *m.Name
}
return ""
}
type SubMessage struct {
Subfield             *string  `protobuf:"bytes,1,opt,name=subfield" json:"subfield,omitempty"`
XXX_NoUnkeyedLiteral struct{} `json:"-"`
XXX_unrecognized     []byte   `json:"-"`
XXX_sizecache        int32    `json:"-"`
}
func (m *SubMessage) Reset()         { *m = SubMessage{} }
func (m *SubMessage) String() string { return proto.CompactTextString(m) }
func (*SubMessage) ProtoMessage()    {}
func (*SubMessage) Descriptor() ([]byte, []int) {
return fileDescriptor_16118676337827bb, []int{1}
}
func (m *SubMessage) XXX_Unmarshal(b []byte) error {
return xxx_messageInfo_SubMessage.Unmarshal(m, b)
}
func (m *SubMessage) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
return xxx_messageInfo_SubMessage.Marshal(b, m, deterministic)
}
func (m *SubMessage) XXX_Merge(src proto.Message) {
xxx_messageInfo_SubMessage.Merge(m, src)
}
func (m *SubMessage) XXX_Size() int {
return xxx_messageInfo_SubMessage.Size(m)
}
func (m *SubMessage) XXX_DiscardUnknown() {
xxx_messageInfo_SubMessage.DiscardUnknown(m)
}
var xxx_messageInfo_SubMessage proto.InternalMessageInfo
func (m *SubMessage) GetSubfield() string {
if m != nil && m.Subfield != nil {
return *m.Subfield
}
return ""
}
type Message struct {
Text                 *string  `protobuf:"bytes,1,opt,name=text" json:"text,omitempty"`
XXX_NoUnkeyedLiteral struct{} `json:"-"`
XXX_unrecognized     []byte   `json:"-"`
XXX_sizecache        int32    `json:"-"`
}
func (m *Message) Reset()         { *m = Message{} }
func (m *Message) String() string { return proto.CompactTextString(m) }
func (*Message) ProtoMessage()    {}
func (*Message) Descriptor() ([]byte, []int) {
return fileDescriptor_16118676337827bb, []int{2}
}
func (m *Message) XXX_Unmarshal(b []byte) error {
return xxx_messageInfo_Message.Unmarshal(m, b)
}
func (m *Message) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
return xxx_messageInfo_Message.Marshal(b, m, deterministic)
}
func (m *Message) XXX_Merge(src proto.Message) {
xxx_messageInfo_Message.Merge(m, src)
}
func (m *Message) XXX_Size() int {
return xxx_messageInfo_Message.Size(m)
}
func (m *Message) XXX_DiscardUnknown() {
xxx_messageInfo_Message.DiscardUnknown(m)
}
var xxx_messageInfo_Message proto.InternalMessageInfo
func (m *Message) GetText() string {
if m != nil && m.Text != nil {
return *m.Text
}
return ""
}
func init() {
proto.RegisterType((*GetMessageRequest)(nil), "xxx.GetMessageRequest")
proto.RegisterType((*SubMessage)(nil), "xxx.SubMessage")
proto.RegisterType((*Message)(nil), "xxx.Message")
}
func init() { proto.RegisterFile("xxx.proto", fileDescriptor_16118676337827bb) }
var fileDescriptor_16118676337827bb = []byte{
// 169 bytes of a gzipped FileDescriptorProto
0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0xe2, 0xe2, 0xac, 0xa8, 0xa8, 0xd0,
0x2b, 0x28, 0xca, 0x2f, 0xc9, 0x17, 0x62, 0xae, 0xa8, 0xa8, 0x50, 0x72, 0xe3, 0x12, 0x74, 0x4f,
0x2d, 0xf1, 0x4d, 0x2d, 0x2e, 0x4e, 0x4c, 0x4f, 0x0d, 0x4a, 0x2d, 0x2c, 0x4d, 0x2d, 0x2e, 0x11,
0x92, 0xe5, 0xe2, 0xca, 0x85, 0x88, 0xc4, 0x67, 0xa6, 0x48, 0x30, 0x2a, 0x30, 0x6a, 0x70, 0x06,
0x71, 0x42, 0x45, 0x3c, 0x53, 0x84, 0x84, 0xb8, 0x58, 0xf2, 0x12, 0x73, 0x53, 0x25, 0x98, 0x15,
0x98, 0x34, 0x38, 0x83, 0xc0, 0x6c, 0x25, 0x0d, 0x2e, 0xae, 0xe0, 0xd2, 0x24, 0xa8, 0x39, 0x42,
0x52, 0x5c, 0x1c, 0xc5, 0xa5, 0x49, 0x69, 0x99, 0xa9, 0x39, 0x30, 0xed, 0x70, 0xbe, 0x92, 0x2c,
0x17, 0x3b, 0x4c, 0x99, 0x10, 0x17, 0x4b, 0x49, 0x6a, 0x45, 0x09, 0x54, 0x09, 0x98, 0x6d, 0x64,
0xcf, 0xc5, 0x09, 0x91, 0xce, 0xcc, 0x4b, 0x17, 0x32, 0xe2, 0xe2, 0x42, 0xb8, 0x4e, 0x48, 0x4c,
0x0f, 0xe4, 0x78, 0x0c, 0xe7, 0x4a, 0xf1, 0x80, 0xc5, 0xa1, 0x82, 0x80, 0x00, 0x00, 0x00, 0xff,
0xff, 0x44, 0xe8, 0x5d, 0x70, 0xe2, 0x00, 0x00, 0x00,
}
// Reference imports to suppress errors if they are not otherwise used.
var _ context.Context
var _ client.Option
var _ server.Option
// Client API for Messaging service
type MessagingService interface {
GetMessage(ctx context.Context, in *GetMessageRequest, opts ...client.CallOption) (*Message, error)
}
type messagingService struct {
clients map[string]client.Client
}
func NewMessagingService(c client.Factory) MessagingService {
if c == nil {
panic("factory is nil")
}
service := &messagingService{
clients: make(map[string]client.Client),
}
service.clients["xxx.Messaging.GetMessage"] = c.Client("xxx.Messaging.GetMessage")
return service
}
func NewMessagingServiceName(name string) MessagingService {
service := &messagingService{
clients: make(map[string]client.Client),
}
service.clients["xxx.Messaging.GetMessage"] = proxy.InitRPC(name, "xxx.Messaging.GetMessage")
return service
}
func (c *messagingService) GetMessage(ctx context.Context, in *GetMessageRequest, opts ...client.CallOption) (*Message, error) {
out := new(Message)
err := c.clients["xxx.Messaging.GetMessage"].Invoke(ctx, in, out, opts...)
if err != nil {
return nil, err
}
return out, nil
}
// Server API for Messaging service
type MessagingHandler interface {
GetMessage(context.Context, *GetMessageRequest) (*Message, error)
}
func RegisterMessagingHandler(s server.Server, hdlr MessagingHandler, opts ...server.HandlerOption) {
type messaging interface {
GetMessage(ctx context.Context, in *GetMessageRequest) (*Message, error)
}
type Messaging struct {
messaging
}
opts = append(opts, server.HandlerName("xxx.Messaging"))
h := &messagingHandler{hdlr}
if err := s.Handle(s.NewHandler(&Messaging{h}, opts...)); err != nil {
panic(err)
}
}
type messagingHandler struct {
MessagingHandler
}
func (h *messagingHandler) GetMessage(ctx context.Context, in *GetMessageRequest) (*Message, error) {
return h.MessagingHandler.GetMessage(ctx, in)
}
app 子目录
其中 main.go 的内容会略微有点不同，调整为调用框架 rpc 相关的初始化和释放函数：rpc.Init() 和 rpc.Shutdown()。
// rpc server main.go
package main
import (
"flag"
"log"
"os"
"os/signal"
"syscall"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/conf"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/server/rpc"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/service"
"git.inke.cn/BackendPlatform/golang/logging"
"git.inke.cn/inkelogic/daenerys"
)
func init() {
configS := flag.String("config", "config/config.toml", "Configuration file")
appS := flag.String("app", "", "App dir")
flag.Parse()
daenerys.Init(
daenerys.ConfigPath(*configS),
)
if *appS != "" {
daenerys.InitNamespace(*appS)
}
}
func main() {
log.Println("yyy start")
defer daenerys.Shutdown()
// init local config
cfg, err := conf.Init()
if err != nil {
logging.Fatalf("service config init error %s", err)
}
// create a service instance
svc := service.New(cfg)
// init and start http server
rpc.Init(svc, cfg)
defer rpc.Shutdown()
sigChan := make(chan os.Signal, 1)
signal.Notify(sigChan, syscall.SIGHUP, syscall.SIGQUIT, syscall.SIGTERM, syscall.SIGINT)
for {
s := <-sigChan
log.Printf("get a signal %s\n", s.String())
switch s {
case syscall.SIGQUIT, syscall.SIGTERM, syscall.SIGINT:
log.Println("yyy server exit now...")
return
case syscall.SIGHUP:
default:
}
}
}
server 子目录
server
└── rpc
└── rpc.go
2 directories, 1 file
在 rpc.go 中，service 的注册与 http 方式不太一样，是通过 xxx.pb.go 中提供的函数来注册的：api.RegisterMessagingHandler()。
// rpc server rpc.go
package rpc
import (
api "git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/api/xxx"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/conf"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/service"
"git.inke.cn/BackendPlatform/golang/logging"
"git.inke.cn/inkelogic/daenerys"
rpcserver "git.inke.cn/inkelogic/daenerys/rpc/server"
rpcplugin "git.inke.cn/inkelogic/daenerys/plugins/rpc"
)
var (
svc *service.Service
rpcServer rpcserver.Server
)
// Init create a rpc server and run it
func Init(s *service.Service, conf *conf.Config) {
svc = s
rpcServer = daenerys.RPCServer()
// add namespace plugin
rpcServer.Use(rpcplugin.Namespace)
api.RegisterMessagingHandler(rpcServer, svc)
// start a rpc server
if err := rpcServer.Start(); err != nil {
logging.Fatalf("rpc server start failed, err %v", err)
}
}
// Close close the resource
func Shutdown() {
if rpcServer != nil {
rpcServer.Stop()
}
if svc != nil {
svc.Close()
}
}
service 子目录
对于 rpc 服务，它所提供的 Service 功能已经在 proto 文件中定义了。可以看到 service.go 文件中的 GetMessage 是与 xxx.proto 中对应的。
service Messaging {
rpc GetMessage (GetMessageRequest) returns (Message);
}
package service
import (
"context"
"fmt"
api "git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/api/xxx"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/conf"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/dao"
"git.inke.cn/BackendPlatform/daenerys-tool/daenerys/yyy/manager"
"github.com/golang/protobuf/proto"
)
// Service represents several business logic(s)
type Service struct {
c *conf.Config
// dao: db handler
dao *dao.Dao
// manager: other client(s), other middleware(s)
mgr *manager.Manager
}
// New new a service and return.
func New(c *conf.Config) (s *Service) {
return &Service{
c:   c,
dao: dao.New(c),
mgr: manager.New(c),
}
}
// Ping check service's resource status
func (s *Service) Ping(ctx context.Context) error {
return s.dao.Ping(ctx)
}
// Close close the resource
func (s *Service) Close() {
if s.dao != nil {
s.dao.Close()
}
if s.mgr != nil {
s.mgr.Close()
}
}
func (s *Service) GetMessage(ctx context.Context, request *api.GetMessageRequest) (*api.Message, error) {
info := fmt.Sprintf("id:%s,name:%s", request.GetMessageId(), request.GetName())
result := &api.Message{Text: proto.String(info + " aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")}
return result, nil
}
需要注意的事项
注意 1
服务部署前需要为项目生成 Godeps 依赖文件，并且需要
保证本地 go build 是通过的
，这样才能将服务正确部署到相应环境上。如果项目是使用 gomod 工具来管理依赖包的话，需要开发者自己保证依赖包的版本是正确的，并能正确运行服务。如果是使用 inkedep 工具管理依赖包的话，请按照以下指引来操作生成 Godeps 文件，并最终提交到项目仓库中。
请确认本地环境已安装了最新的
inkedep
工具。
# 生成依赖文件
cd app
inkedep save
注意 2
代码生成工具支持对生成的 http 服务进行增量更新，重新执行创建项目时候的命令即可。它不会覆盖之前生成的 service 目录下相关的文件。但是 rpc 服务暂时不支持。
注意 3
为了规范开发的代码，请大家在正式开发前仔细阅读下公司的代码规范，避免踩坑！！！
公司代码规范
