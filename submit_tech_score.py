#!/usr/bin/env python3
"""
技术方案评分提交脚本
用于向 /api/tech/score/submit 接口发送POST请求
"""

import json
import argparse
import requests
import sys
from typing import Optional


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="提交技术方案评分到全栈质量平台",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python submit_tech_score.py --url http://10.38.219.120:80 \
        --tech-doc-name "订单系统技术方案" \
        --tech-doc-link "https://confluence.xiaomi.com/pages/viewpage.action?pageId=123456" \
        --submitter "张三" \
        --business-line "电商" \
        --product-score 85.5 \
        --backend-score 90.0 \
        --frontend-score 88.0 \
        --test-score 92.5 \
        --global-score 89.0 \
        --global-level "优秀"
        
    python submit_tech_score.py --url http://10.38.219.120:80 --from-file data.json
"""
    )
    
    # 必填参数
    parser.add_argument(
        "--url",
        required=True,
        help="API服务器地址，例如: http://10.38.219.120:80"
    )
    
    # 文档信息
    parser.add_argument(
        "--tech-doc-name",
        help="技术文档名称"
    )
    parser.add_argument(
        "--tech-doc-link",
        help="技术文档链接"
    )
    parser.add_argument(
        "--submitter",
        help="提交人"
    )
    parser.add_argument(
        "--business-line",
        help="业务线"
    )
    
    # 评分参数
    parser.add_argument(
        "--product-score",
        type=float,
        help="产品视角评分"
    )
    parser.add_argument(
        "--backend-score",
        type=float,
        help="后端视角评分"
    )
    parser.add_argument(
        "--frontend-score",
        type=float,
        help="前端视角评分"
    )
    parser.add_argument(
        "--test-score",
        type=float,
        help="测试视角评分"
    )
    parser.add_argument(
        "--global-score",
        type=float,
        help="全局总分"
    )
    parser.add_argument(
        "--global-level",
        help="全局等级（优秀/良好/一般/风险）"
    )
    
    # 从文件读取
    parser.add_argument(
        "--from-file",
        help="从JSON文件读取参数，文件格式参考示例"
    )
    
    return parser.parse_args()


def load_from_json_file(file_path: str) -> dict:
    """从JSON文件加载参数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON格式无效 - {e}")
        sys.exit(1)


def build_request_data(args: argparse.Namespace) -> dict:
    """构建请求数据"""
    if args.from_file:
        # 从文件加载
        file_data = load_from_json_file(args.from_file)
        return file_data
    else:
        # 从命令行参数构建
        data = {}
        
        # 文档信息
        if args.tech_doc_name:
            data["techDocName"] = args.tech_doc_name
        if args.tech_doc_link:
            data["techDocLink"] = args.tech_doc_link
        if args.submitter:
            data["submitter"] = args.submitter
        if args.business_line:
            data["businessLine"] = args.business_line
        
        # 评分信息
        if args.product_score is not None:
            data["productScore"] = args.product_score
        if args.backend_score is not None:
            data["backendScore"] = args.backend_score
        if args.frontend_score is not None:
            data["frontendScore"] = args.frontend_score
        if args.test_score is not None:
            data["testScore"] = args.test_score
        if args.global_score is not None:
            data["globalScore"] = args.global_score
        if args.global_level:
            data["globalLevel"] = args.global_level
        
        return data


def send_request(api_url: str, data: dict) -> None:
    """发送HTTP请求"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        print(f"正在发送请求到: {api_url}")
        print(f"请求数据:\n{json.dumps(data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容:\n{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ 请求成功！")
        else:
            print(f"\n❌ 请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"错误: 无法连接到服务器 {api_url}")
        print("请检查:")
        print("  1. 服务器地址是否正确")
        print("  2. 服务器是否正在运行")
        print("  3. 网络连接是否正常")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("错误: 请求超时")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"错误: 请求异常 - {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: 响应不是有效的JSON格式")
        print(f"原始响应: {response.text}")
        sys.exit(1)


def validate_data(data: dict) -> bool:
    """验证请求数据"""
    required_fields = [
        "techDocName",
        "techDocLink",
        "submitter",
        "businessLine",
        "productScore",
        "backendScore",
        "frontendScore",
        "testScore",
        "globalScore",
        "globalLevel"
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        print("错误: 缺少以下必填字段:")
        for field in missing_fields:
            print(f"  - {field}")
        print("\n请通过命令行参数或JSON文件提供这些字段")
        return False
    
    return True


def main() -> None:
    """主函数"""
    args = parse_arguments()
    
    # 构建API URL（注意：服务器配置了 context-path=/fullstack）
    api_url = f"{args.url.rstrip('/')}/fullstack/api/tech_plan/score/submit"
    
    # 构建请求数据
    data = build_request_data(args)
    
    # 验证数据
    if not validate_data(data):
        sys.exit(1)
    
    # 发送请求
    send_request(api_url, data)


if __name__ == "__main__":
    main()
