#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/interrupt.h>
#include <linux/gpio.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>

#define DRIVER_NAME "Tact Switch/LED"
#define TS_IN 2
#define LED_OUT 4

static dev_t tsled_device;
static struct cdev tsled_cdevice;

/* Display message when device is opened */
static int tsled_open(struct inode *i, struct file *f) {
	printk("%s opened\n",DRIVER_NAME);
	return 0;
}

/* Display message when device is released */
static int tsled_release(struct inode *i, struct file *f) {
	printk("%s closed\n",DRIVER_NAME);
	return 0;
}

/* Read state of tact switch */
/* -> 0 when pushed */
static ssize_t tsled_read(struct file *file, char __user *buf, size_t length, loff_t *offset) {
	unsigned char read_val = gpio_get_value(TS_IN);
	int read_length = (length < sizeof(read_val)) ? length : sizeof(read_val);
/* copy data from kernel space to user space */
	if (copy_to_user(buf, &read_val, read_length))
		return -EFAULT;
	return read_length;
}

/* Turn on/off LED */
static ssize_t tsled_write(struct file *file, const char __user *buf, size_t length, loff_t *offset) {
	unsigned char write_val;
	int write_length = (length < sizeof(write_val)) ? length : sizeof(write_val);
	if (copy_from_user(&write_val, buf, write_length))
		return -EFAULT;
	if (write_val == 0) {
		gpio_set_value(LED_OUT, 0);
	}else if (write_val == 1){
		gpio_set_value(LED_OUT, 1);
	}else {
		printk("eroor number: %d: please press 0 or 1\n", write_val);
	}
	gpio_free(TS_IN);
	gpio_free(LED_OUT);
	printk("data write: %d\n",write_val);
	return write_length;	
}

/* Operations for this device */
static struct file_operations tsled_fops = {
	.owner = THIS_MODULE,
	.open = tsled_open,
	.read = tsled_read,
	.write = tsled_write,
	.release = tsled_release,
};

/* Module initialization */
static int tsled_init(void) {
	int ret_value;
/* set GPIO directions */
	gpio_direction_input(TS_IN);
	gpio_direction_output(LED_OUT,0);

/* Register device */
	ret_value = alloc_chrdev_region(&tsled_device, 0, 1, DRIVER_NAME);
	if (ret_value < 0) {
		printk("%s: alloc_chrdev_region failed (%d)\n", __FUNCTION__, ret_value);
		gpio_free(TS_IN);
		gpio_free(LED_OUT);
		return ret_value;
	}

/* Register character device */
	cdev_init(&tsled_cdevice, &tsled_fops);
	ret_value = cdev_add(&tsled_cdevice, tsled_device, 1);
	if (ret_value < 0) {
		printk("%s: cdev_add failed (%d)\n", __FUNCTION__, ret_value);
		unregister_chrdev_region(tsled_device, 1);
		gpio_free(TS_IN);
		gpio_free(LED_OUT);		
		return ret_value;
	}

/* Success - show major and minor numbers */
	printk("%s loaded: Major=%d, Minor=%d\n", DRIVER_NAME, MAJOR(tsled_device), MINOR(tsled_device));

	return 0;
}

/* Free resources when the module is unloaded */
static void tsled_cleanup(void)
{
	cdev_del(&tsled_cdevice);
	unregister_chrdev_region(tsled_device, 1);
	gpio_free(TS_IN);
	gpio_free(LED_OUT);		
	printk("%s unloaded\n",DRIVER_NAME);
}

module_init(tsled_init);
module_exit(tsled_cleanup);

MODULE_LICENSE("GPL");