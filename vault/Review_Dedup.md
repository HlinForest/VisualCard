# 判重自检（每周过一遍，插件不做自动判重，靠这页手工清）

## 1. 疑似同一人（电话或邮箱相同，文件却有两个）

```dataview
TABLE WITHOUT ID file.link AS "文件", name AS "姓名", company AS "公司",
  join(phones, ", ") AS "电话", join(emails, ", ") AS "邮箱"
FROM #contact
GROUP BY join(phones, ", ") + join(emails, ", ")
WHERE length(rows) > 1
```

## 2. 同名待确认（同名但电话全不同或全空 → 进 inbox/_review/ 或手动合）

```dataview
TABLE WITHOUT ID file.link AS "文件", name AS "姓名", company AS "公司",
  role AS "职位", join(phones, ", ") AS "电话"
FROM #contact
SORT name ASC
```

逐行看 `姓名` 相同的：同一人 → 旧公司/职位追加进 `career_history` 后删重复文件；
不同人 → 备注区分（如公司后缀）。

## 3. 缺关键字段（电话邮箱全空，创的卡基本不可检索）

```dataview
TABLE WITHOUT ID file.link AS "文件", name AS "姓名", company AS "公司"
FROM #contact
WHERE length(phones) = 0 AND length(emails) = 0
```

补录后删此行，具体卡重跑一次插件解析即可。
