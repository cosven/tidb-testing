// httpserver is a POC example for etcd/v3/pkg/proxy
package main

import (
	"github.com/pingcap/log"

	"fmt"
	"net/http"
	"net/url"
	"time"

	"go.etcd.io/etcd/v3/pkg/proxy"
)

func startHttpServer(port int) {

	pingHandler := func(w http.ResponseWriter, r *http.Request) {
		log.S().Info("/ping")
		fmt.Fprint(w, "pong\n")
	}

	http.HandleFunc("/ping", pingHandler)

	if err := http.ListenAndServe(fmt.Sprintf(":%d", port), nil); err != nil {
		panic(err.Error())
	}
	log.S().Info("http server listening on ", port)
}

func startProxyServer(addr string, targetAddr string) {
	url, err := url.Parse(addr)
	if err != nil {
		panic(err.Error())
	}
	targetUrl, err := url.Parse(targetAddr)
	if err != nil {
		panic(err.Error())
	}
	config := proxy.ServerConfig{
		Logger: log.L(),
		From:   *url,
		To:     *targetUrl,
	}
	server := proxy.NewServer(config)
	select {
	case err := <-server.Error():
		panic(fmt.Sprintf("start proxy server failed, %s", err.Error()))
	case <-time.After(time.Second):
		log.S().Info("proxy server started at ", addr)
	}
	server.DelayTx(1*time.Second, 1*time.Second)
}

func main() {
	defer log.Sync()

	port := 8080
	proxyPort := 8888

	addr := fmt.Sprintf("http://0.0.0.0:%d", port)
	proxyAddr := fmt.Sprintf("http://0.0.0.0:%d", proxyPort)

	// TODO: close/shutdown these two server properly
	// https://stackoverflow.com/a/40041517/4302892
	go startHttpServer(port)
	go startProxyServer(proxyAddr, addr)

	doneCh := make(chan struct{}, 1)
	<-doneCh
}
