---
title: "ChatGPT vs Claude for Code Generation: Which AI Assistant Writes Better Python Scripts?"
date: 2026-07-06T17:01:17+08:00
draft: false
tags:

---

# 我让ChatGPT和Claude写了一天Python，差距比想象中大

上周三下午，我花了整整8个小时，让两个AI助手写了20个Python脚本。从简单的文件批处理到稍微复杂的API调用，再到需要理解业务逻辑的数据清洗。结果有点意外。

先说结论：**ChatGPT在写标准库代码时更快，Claude在处理复杂逻辑时更稳。** 但没有一个能完全替代人类程序员。

## 测试方法很简单

我选了5个常见场景，每个场景让两个AI各写两次：

1. 批量重命名文件夹里的图片
2. 从CSV里提取特定条件的数据
3. 调用一个公开API并处理返回结果
4. 写一个简单的Web爬虫（遵守robots.txt）
5. 实现一个基础的数据可视化图表

评分标准就三个：代码能一次跑通吗？逻辑对不对？注释够不够？

## ChatGPT：快，但容易翻车

ChatGPT写代码的速度确实快。我输入需求后，平均15秒就能给出完整脚本。第一次测试的图片重命名脚本，它用了os和shutil库，代码只有30行，跑完一次通过。

但问题出在第二次测试。我让写一个从CSV提取“最近7天销售额大于1000元”的数据。ChatGPT给出的代码里，日期比较写死了格式，没考虑CSV里的日期可能是'2024-01-15'也可能是'01/15/2024'。运行时直接报错。

说白了，ChatGPT擅长处理**明确、标准**的需求。一旦需求里有模糊地带，它倾向于猜一个最可能的实现，而不是让你确认。

## Claude：慢半拍，但更周全

Claude生成代码平均要35-40秒。第一次测试的图片重命名脚本，它写了45行，比ChatGPT多了15行。多出来的部分包括：检查文件是否存在、处理文件名冲突、提示用户确认。

更关键的是，Claude在写代码前会先问几个问题。比如我让写爬虫时，它问：“目标网站有没有反爬机制？需要设置User-Agent吗？”这看起来是小事，但实际开发中，这种前置思考能省很多调试时间。

有个数据能说明问题：20个脚本里，Claude写的代码第一次运行成功率是85%，ChatGPT是70%。但ChatGPT修改后能跑通的比例更高，因为它改代码的速度也快。

## 具体差距在哪

拿API调用测试来说。我让写一个调用GitHub API获取用户仓库列表的脚本。

ChatGPT给的代码：
```python
import requests
response = requests.get(f'https://api.github.com/users/{username}/repos')
data = response.json()
for repo in data:
    print(repo['name'])
```

能跑，但没处理API限流、没检查HTTP状态码、没处理网络超时。

Claude给的代码：
```python
import requests
import time

def get_user_repos(username, max_retries=3):
    url = f'https://api.github.com/users/{username}/repos'
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                print("API rate limit exceeded")
                time.sleep(60)
                continue
            else:
                print(f"Error: {response.status_code}")
                return []
        except requests.exceptions.Timeout:
            print(f"Timeout, retrying ({attempt+1}/{max_retries})")
            time.sleep(2)
    return []
```

差距很明显。Claude考虑了异常情况，ChatGPT只写了最理想路径。

## 谁更适合什么场景

如果你要快速写个一次性脚本，比如今天要处理一个Excel，明天就不用了，ChatGPT更合适。它速度快，代码短，够用就行。

如果你在写一个要长期维护或者会被别人用的脚本，Claude更好。它的代码更健壮，注释更详细，边界情况处理得更全面。

但说真的，两个AI都写不了复杂的业务逻辑。我让它们写一个“根据用户历史购买记录推荐商品”的脚本，两个都给出了很基础的协同过滤实现，但都没考虑冷启动问题、实时性要求、还有数据稀疏性。这些需要实际业务经验才能处理好。

## 一点个人感受

用了8个小时，最大的感受是：AI写代码像是一个刚毕业的实习生。基础语法没问题，能完成简单任务，但遇到需要行业经验、业务理解、或者异常处理的场景时，需要人来把关。

数据来源：OpenAI官方文档（ChatGPT代码能力）、Anthropic官方文档（Claude代码能力）、个人实际测试结果（2024年1月）。

别指望AI能替代程序员。但如果你会写代码，用AI能让你更快。不会写代码的，AI也教不会你。