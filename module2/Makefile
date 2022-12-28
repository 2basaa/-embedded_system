KERNEL_BUILD_DIR=/lib/modules/$(shell uname -r)/build
obj-m := kadai10.o
all:
	make -C $(KERNEL_BUILD_DIR) M=$(PWD) modules
clean:
	make -C $(KERNEL_BUILD_DIR) M=$(PWD) clean