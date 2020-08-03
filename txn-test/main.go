package main

import (
	"database/sql"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"strings"
	"time"
)

func MustExec(s *sql.DB, q string) (result sql.Result) {
	// FIXME:
	for _, stmt := range strings.Split(q, ";") {
		stmt = strings.TrimSpace(stmt)
		if stmt == "" {
			continue
		}
		res, err := s.Exec(stmt)
		if err != nil {
			panic(err)
		}
		result = res
	}
	return result
}

func table1(s *sql.DB) {
	MustExec(s, `
drop table if exists t1;
create table t1 (i int, j int, k int, unique index unq_j (j));
insert into t1 values (1, 1, 1), (2, 2, 2);
`)
}

func table2(s *sql.DB) {
	MustExec(s, `
 drop table if exists t1;
 create table t1 (i int key, j int, k int, unique index unq_j (j));
 insert into t1 values (1, 1, 1), (2, 2, 2);
 `)
}

func main() {
	DSN := "root:@tcp(172.16.4.82:30488)/test"
	// DSN := "root:@tcp(127.0.0.1:3306)/test"
	s1, err := sql.Open("mysql", DSN)
	if err != nil {
		panic("connect failed")
	}
	defer s1.Close()
	s2, err := sql.Open("mysql", DSN)
	if err != nil {
		panic("connect failed")
	}
	defer s2.Close()

	table1(s1)
	//table2(s1)

	MustExec(s1, `
begin ;
insert into t1 values (3, 3, 3);
`)
	start := time.Now().Unix()
	fmt.Printf("start s2: %d\n", start)
	go MustExec(s2, `
set innodb_lock_wait_timeout=5;
begin ;
update t1 set k = 33 where j = 3;
`)
	time.Sleep(1)
	fmt.Printf("wait time: %d\n", time.Now().Unix()-start)
	MustExec(s1, "commit;")
	MustExec(s2, "commit;")
}
