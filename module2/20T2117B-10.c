#include <sys/ioctl.h>
#include <sys/types.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <unistd.h>

static unsigned char read_prev = 1;
static unsigned char write_status = 0;
int sleep_time = 1;/*sleep time = 1*/
/*kadai3 Read*/
u_char Read()
{
	/*file raad mode*/
	FILE *fp = fopen("/dev/tsled", "r");/*open file*/
	unsigned char v;

	if (fp != NULL) {
		if (fread(&v,sizeof(v),1,fp) == 1) {
			printf("Read Status is %d\n",v);/*write 0 or 1*/
		}else
			printf("Device read error (%d)\n", errno);/*not 0 or 1*/
	}
	fclose(fp);/*close file*/
	return v;/*v = 0 or 1*/
}
/*kadai3 Write*/
u_char Write(unsigned char v) /*get 0 or 1*/
{
	/*read and write mode*/
	FILE *fp = fopen("/dev/tsled", "r+");/*open file*/
	unsigned char status;

	if (fp != NULL) {
		if (fwrite(&v,sizeof(v),1,fp) == 1) {
			status = v;/*statrus = v*/
			printf("Write Status is %d\n",v);/*write 0 or 1*/
		}
		else
			printf("Device write error (%d)\n", errno);
	}
	fclose(fp);/*close file*/
	return status;/*get 0 or 1*/
}
/*kadai3 process*/
void kadai3()
{
	unsigned char v = Read();/*get 0 or 1*/
	printf("Prev is  (%d)\n", read_prev);
	/*prev_readData=0, current_readData=1*/
	if (read_prev == 0 && v == 1) {
		if (write_status == 0) {
			/*write_status 0→1*/
			write_status = Write(1);
		}else {
			/*write_status 1→0*/
			write_status = Write(0);
		}
	}
	read_prev = v;/*change read_prev*/
}
/*execution function*/
int main()
{
	Write(0);/*led initialization*/
	for (int i = 0; i < 10000; i += 1){
		/*can active kadai3 count 10000*/
		sleep(sleep_time);
		kadai3();
	}
	return 0;
}
