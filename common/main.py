import json
from typing import Any, Dict

from deepdiff import DeepDiff


def clean_path(path: str) -> str:
    """
    移除 root[...] 的前缀，返回更干净的字段路径
    """
    if path.startswith("root"):
        path = path[4:]  # 去掉 root
        # 去掉开头的方括号，变成 a 或 b[1] 的形式
        path = path.replace("][", ".").replace("[", "").replace("]", "")
        if path.startswith("."):
            path = path[1:]
    return path


def diff_to_readable(d1: Any, d2: Any, ignore_order=True) -> Dict[str, Any]:
    diff = DeepDiff(d1, d2, ignore_order=ignore_order)
    result = {'val_changed': {}, 'type_changed': {}, 'added': [], 'removed': []}

    for k, v in diff.get('values_changed', {}).items():
        # print(k)
        result['val_changed'][clean_path(k)] = f"{v['old_value']} -> {v['new_value']}"

    for k, v in diff.get('type_changes', {}).items():
        # result['changed'][clean_path(k)] = {'old': v['old_type'].__name__, 'new': v['new_type'].__name__}
        result['type_changed'][clean_path(k)] = f"{v['old_type'].__name__} -> {v['new_type'].__name__}"

    result['dict_added'] = [clean_path(p) for p in diff.get('dictionary_item_added', [])]
    iter_item_added = {}
    for k, v in diff.get('iterable_item_added', {}).items():
        iter_item_added[clean_path(k)] = v
    result['iter_added'] = iter_item_added

    result['dict_removed'] = [clean_path(p) for p in diff.get('dictionary_item_removed', [])]
    iter_item_removed = {}
    for k, v in diff.get('iterable_item_removed', {}).items():
        iter_item_added[clean_path(k)] = v
    result['iter_removed'] = iter_item_removed
    return result


if __name__ == '__main__':
    d1 = {
        'f1': 1,
        'f2': 'a',
        'f4': {
            'f1': 1,
        },
        1: 1,
        'f5': [1, 2],
        'f6': 'abc',
    }
    d2 = {
        'f1': 5,
        'f3': 1,
        'f2': 1,
        'f4': {
            'f1': 11,
        },
        1: 3,
        'f5': [1, 9, 3, 4]
    }
    result = diff_to_readable(d1, d2)
    with open("../diff.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
