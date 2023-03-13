---
date: 2023-03-08 08:39:33 +0900
layout: post
title: "[WebServer/Apache] Mutex And Semaphore"
tags: [Apache, OHS, Mutex, Semaphore]
typora-root-url: ..
---

# 1. 개요

Apache, OHS 의 SSLSessionCache 에서 사용되는 Mutex와 Semaphore 에 대해서 간략하게 알아본다.



# 2. 설명

고객의 `ssl.conf` 설정값으로 다음의 기본값이 지정되었다.

```
#   Inter-Process Session Cache:
#   Configure the SSL Session Cache: First the mechanism
#   to use, second the expiring timeout (in seconds) and third
#   the mutex to be used.
    SSLSessionCache "shmcb:${ORACLE_INSTANCE}/servers/${COMPONENT_NAME}/logs/ssl_scache(512000)"
    SSLSessionCacheTimeout  300
    <IfModule !mpm_winnt_module>
      Mutex pthread ssl-cache
    </IfModule>
```

- SSLSessionCache : Mechanism
- SSLSessionCacheTimeout : Expiring timeout (in seconds)
- Mutex : Mutex to be used



다음의 Error와 함께, 기동이 되지 않았다.

```
(13)Permission denied: AH00023: Couldn't create the ssl-cache mutex
```



해당 사례를 살펴보기 위해 Apache 컴파일 소스를 뒤져보았다.



# 3. Mutex

* Mutual Exclusion (상호 배제)
* 공유 자원에, Only 1개의 Thread만 접근 가능하도록 하는 기법
* 1개 Thread가 자원 접근이 “가능할 때”  Lock을 걸고 공유 자원이 있는 “임계 영역(Critical Section)”에 접근
* Lock을 가지고 있는 Thread만이 Lock Release 하여 빠져나올 수 있음



chatgpt의 example code를 보면,

```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class MutexExample {
    private static int counter = 0;
    private static Lock lock = new ReentrantLock();

    public static void main(String[] args) throws InterruptedException {
        Thread thread1 = new Thread(new IncrementThread());
        Thread thread2 = new Thread(new IncrementThread());

        thread1.start();
        thread2.start();

        thread1.join();
        thread2.join();

        System.out.println("Final counter value: " + counter);
    }

    static class IncrementThread implements Runnable {
        @Override
        public void run() {
            for (int i = 0; i < 100000; i++) {
                lock.lock();
                try {
                    counter++;
                } finally {
                    lock.unlock();
                }
            }
        }
    }
}
```



공통자원 lock을 Thread 1개만 소유할 수 있어, Mutex 가 증명된다.



# 4. Semaphore

* 기찻길에서 선로를 가리키는 “깃발” 이 어원.
* Mutex와 상당히 유사하나 다른 점은,
  * Mutex는 임계 영역에 접근하기 위해, 1개 Thread가 Lock을 소유하고 있다.
  * Semaphore는 Lock을 소유하지 않고, 접근 가능한 수(count)를 보고 진입한다.
  * Semaphore에 접근하려는 Thread 만큼 count를 줄이고, 0보다 클 경우 임계 영역에 접근한다.
  * 즉, Semaphore는 count 만큼 누구나, 동시에 들어설 수 있다.
* count(동시 접근 가능 수)가 1인 경우, binary mutex라고 함.



example code.

```java
import java.util.concurrent.Semaphore;

public class SemaphoreExample {
    private static final int NUM_THREADS = 10;
    private static Semaphore semaphore = new Semaphore(3);

    public static void main(String[] args) throws InterruptedException {
        Thread[] threads = new Thread[NUM_THREADS];

        for (int i = 0; i < NUM_THREADS; i++) {
            threads[i] = new Thread(new WorkerThread(i));
            threads[i].start();
        }

        for (int i = 0; i < NUM_THREADS; i++) {
            threads[i].join();
        }

        System.out.println("All threads have finished.");
    }

    static class WorkerThread implements Runnable {
        private int id;

        public WorkerThread(int id) {
            this.id = id;
        }

        @Override
        public void run() {
            try {
                System.out.println("Thread " + id + " is waiting for a permit.");
                semaphore.acquire();
                System.out.println("Thread " + id + " has acquired a permit.");
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                System.out.println("Thread " + id + " is releasing the permit.");
                semaphore.release();
            }
        }
    }
}
```



lock은 없고, Thread 10개 중에서 Semaphore count 3만큼만 참여한다.



# 5. View Source In httpd

httpd/modules/ssl/ssl_private.h 에서 ssl-cache 정의를 확인할 수 있다.

```c
/**  Mutex Support  */
int          ssl_mutex_init(server_rec *, apr_pool_t *);
int          ssl_mutex_reinit(server_rec *, apr_pool_t *);
int          ssl_mutex_on(server_rec *);
int          ssl_mutex_off(server_rec *);

int          ssl_stapling_mutex_reinit(server_rec *, apr_pool_t *);

/* mutex type names for Mutex directive */
#define SSL_CACHE_MUTEX_TYPE    "ssl-cache"
#define SSL_STAPLING_CACHE_MUTEX_TYPE "ssl-stapling"
#define SSL_STAPLING_REFRESH_MUTEX_TYPE "ssl-stapling-refresh"
```



httpd/modules/ssl/ssl_engine_mutex.c 에서 mutex 를 통한 lock 구현 호출 지점

```c
 if ((rv = ap_global_mutex_create(&mc->pMutex, NULL, SSL_CACHE_MUTEX_TYPE,
                                     NULL, s, s->process->pool, 0))


 if ((rv = apr_global_mutex_child_init(&mc->pMutex,
                                          lockfile,
                                          p)) != APR_SUCCESS) 

										  
 if ((rv = apr_global_mutex_lock(mc->pMutex)) != APR_SUCCESS) {
        ap_log_error(APLOG_MARK, APLOG_WARNING, rv, s, APLOGNO(02026)
                     "Failed to acquire SSL session cache lock");

					 
 if ((rv = apr_global_mutex_unlock(mc->pMutex)) != APR_SUCCESS) {
        ap_log_error(APLOG_MARK, APLOG_WARNING, rv, s, APLOGNO(02027)
                     "Failed to release SSL session cache lock");
```



httpd/server/util_mutex.c 에서 mutex 구현과 다시 호출 지점이 확인된다.

```c
AP_DECLARE(apr_status_t) ap_global_mutex_create(apr_global_mutex_t **mutex,
                                                const char **name,
                                                const char *type,
                                                const char *instance_id,
                                                server_rec *s, apr_pool_t *p,
                                                apr_int32_t options)
{

...
    rv = apr_global_mutex_create(mutex, fname, mxcfg->mech, p);
...
    rv = ap_unixd_set_global_mutex_perms(*mutex);
```



# 6. View Source In apr

여기서부터는 apr source.

apr/locks/unix/global_mutex.c

```c
APR_DECLARE(apr_status_t) apr_global_mutex_create(apr_global_mutex_t **mutex,
                                                  const char *fname,
                                                  apr_lockmech_e mech,
                                                  apr_pool_t *pool)
{

...
    rv = apr_proc_mutex_create(&m->proc_mutex, fname, mech, m->pool);
...
	rv = opr_thread_mutex_create(&m->thread_mutex, APR_THREAD_MUTEX_DEFAULT, m->pool);
```



apr/locks/unix/proc_mutex.c

```c
APR_DECLARE(apr_status_t) apr_proc_mutex_create(apr_proc_mutex_t **mutex,
                                                const char *fname,
                                                apr_lockmech_e mech,
                                                apr_pool_t *pool)
{
...
    if ((rv = proc_mutex_create(new_mutex, mech, fname)) != APR_SUCCESS)
...

static apr_status_t proc_mutex_pthread_create(apr_proc_mutex_t *new_mutex,  const char *fname)
{
    apr_status_t rv;
    int fd;
    pthread_mutexattr_t mattr;

    fd = open("/dev/zero", O_RDWR);
    if (fd < 0) {
        return errno;
    }

```



proc_mutex.c 까지 소스를 추적하였는데, `proc_mutex_pthread_create` 메서드를 호출하는 지점을 찾지못하였다.

그러나, mutex lock 생성을 위해 `/dev/zero` 을 필요로 하는 것은 확인은 되었다.



# 7. Outcome

고객의 경우, 응답을 중지하여 해당 사례를 끝마치지 못하였지만

`/dev/zero` 권한을 변경하여 해당 이슈 재현이 가능한 점을 보아 `/dev/zero` 가 이슈의 원인이었다.



```sh
$ ls -al /dev/zero
crw-rw-rw- 1 root root 1, 5 Mar  2 11:24 /dev/zero

$ sudo chmod 666 /dev/zero

$ ls -al /dev/zero
crw-rw-r-- 1 root root 1, 5 Mar  2 11:24 /dev/zero
```

zero 파일 권한 기본값은 666이며, others(apache 설치 계정) 권한을 4로 지정하여 write 를 제거하면 Mutex 생성 불가 이슈가 재현되었다.
