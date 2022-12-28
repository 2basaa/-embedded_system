#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/interrupt.h>
#include <linux/gpio.h>

/* input pin GPIO2 */
#define G_IN 2

/*output pin GPIO4*/
#define G_OUT 4

/* interrupt handler */
static irqreturn_t button_irq(int irq, void *dev_id) {
  printk("%s: GPIO Value=%d\n", __FUNCTION__, gpio_get_value(G_IN));
  if (gpio_get_value(G_IN) == 1){
    gpio_set_value(G_OUT, 0);
  }else {
    gpio_set_value(G_OUT, 1);
  }
  return IRQ_HANDLED;
}

/* Initialization when module is loaded */
static int mymodule_init(void) {  
  int ret_value;
  printk("%s called\n", __FUNCTION__);
/* set G_IN to input mode */
  gpio_direction_input(G_IN);
  gpio_direction_output(G_OUT, 0);

/* register interrupt handler */
/* gpio_to_irq(): change GPIO number to IRQ number */
/* IRQF_SHARED: enable interrupt sharing */
/* IRQF_TRIGGER_RISING: interrupt triggered on 0->1 changes to G_IN */
/* IRQF_TRIGGER_FALLING: interrupt triggered on 1->0 changes to G_IN */
  ret_value = request_irq(gpio_to_irq(G_IN), button_irq,
    IRQF_SHARED|IRQF_TRIGGER_RISING|IRQF_TRIGGER_FALLING,
	"GPIO button", (void *)button_irq);
  if (ret_value < 0) {
    printk("%s: request_irq failed (%d)\n", __FUNCTION__, ret_value);
	/*gpio_free(G_IN);
  gpio_free(G_OUT);*/
    return ret_value;
  }
  return 0;
}

/* free IRQ, GPIO resources when module is unloaded */
static void mymodule_cleanup(void) {
  printk("%s called\n", __FUNCTION__);
  free_irq(gpio_to_irq(G_IN), (void *)button_irq);
  gpio_free(G_IN);
  gpio_free(G_OUT);
  gpio_direction_output(G_OUT, 0);
}

module_init(mymodule_init);
module_exit(mymodule_cleanup);

MODULE_LICENSE("GPL");