#ifndef __PERF_CONFIG_H
#define __PERF_CONFIG_H

#include <stdbool.h>
#include <linux/list.h>

struct perf_config_item {
	char *name;
	char *value;
	struct list_head node;
};

struct perf_config_section {
	char *name;
	struct list_head items;
	struct list_head node;
};

struct perf_config_set {
	struct list_head sections;
};

struct perf_config_set *perf_config_set__new(void);
void perf_config_set__delete(struct perf_config_set *set);
void perf_config__init(void);
void perf_config__exit(void);
void perf_config__refresh(void);

/**
 * perf_config_sections__for_each - iterate thru all the sections
 * @list: list_head instance to iterate
 * @section: struct perf_config_section iterator
 */
#define perf_config_sections__for_each_entry(list, section)	\
        list_for_each_entry(section, list, node)

/**
 * perf_config_items__for_each - iterate thru all the items
 * @list: list_head instance to iterate
 * @item: struct perf_config_item iterator
 */
#define perf_config_items__for_each_entry(list, item)	\
        list_for_each_entry(item, list, node)

/**
 * perf_config_set__for_each - iterate thru all the config section-item pairs
 * @set: evlist instance to iterate
 * @section: struct perf_config_section iterator
 * @item: struct perf_config_item iterator
 */
#define perf_config_set__for_each_entry(set, section, item)			\
	perf_config_sections__for_each_entry(&set->sections, section)		\
	perf_config_items__for_each_entry(&section->items, item)

#endif /* __PERF_CONFIG_H */
