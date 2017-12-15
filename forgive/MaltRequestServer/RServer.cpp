#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <sys/socket.h>
#include <curl/curl.h>

// Log out stream
FILE *logstream = stdout;
// close tag
bool Is_close_server = false;
// Sub process ID
__pid_t subpid;
void PutLog(const char *logstr,
						FILE *stream = logstream)
{
	time_t timer;
	time(&timer);
	fprintf(stream, // Out stream
					"%s\e[1mLog: %s\e[0m\n",
					ctime(&timer), // Time
					logstr);			 // Error String
}

void PutError(const char *errstr = "Requested server runtime error",
							FILE *stream = logstream)
{
	time_t timer;
	time(&timer);
	fprintf(stream, // Out stream
					"%s\e[31;1mError: \e[0m\e[1m%s\e[0m\n",
					ctime(&timer), // Time
					errstr);			 // Error String
}

void Server_Run()
{
_Init:
	subpid = fork();
	if (subpid == 0)
	{
		try
		{
		}
		catch (...)
		{
			PutError("Request error(ReBooted)");
			goto _Init;
		}
	}
	else if (subpid > 0)
	{
		time_t timer;
		time(&timer);
		fprintf(logstream,
						"%sLog: New Sub process(pid:%i)\n",
						ctime(&timer), subpid);
		// 收到关闭请求后，关掉
		// 如果tag被标记为true，则退出
		while (Is_close_server)
		//while (!Is_close_server)
		{
			sleep(5000);
			// 检查Sub process，如果粗问题（崩）了，就重启
		}
	}
	else
	{
		PutError("New Process Error(ReBooted)");
		goto _Init;
	}
}

int main(int argc, char **argv)
{
	curl_global_init(CURL_GLOBAL_ALL);
	Server_Run();
	curl_global_cleanup();
	return 0;
}
