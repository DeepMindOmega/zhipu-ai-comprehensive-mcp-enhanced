const ZhipuMCPTools = require('../clawd/skills/zhipu-mcp-tools/index.js');

async function quickTest() {
  console.log('开始快速测试智谱AI MCP工具...');
  
  const zhipuTools = new ZhipuMCPTools();
  
  // 测试1: 网页分析
  console.log('\n1. 测试网页分析功能...');
  try {
    const webpageResult = await zhipuTools.analyzeWebpage('https://www.baidu.com');
    console.log('   状态:', webpageResult.success ? '✓ 成功' : '✗ 失败');
    if(webpageResult.success) {
      console.log('   内容长度:', webpageResult.result.summary.length, '字符');
    } else {
      console.log('   错误:', webpageResult.error);
    }
  } catch (error) {
    console.log('   错误:', error.message);
  }
  
  // 测试2: 文本生成
  console.log('\n2. 测试文本生成功能...');
  try {
    const textResult = await zhipuTools.generateText('简要介绍人工智能的发展历程，不超过50字', 'glm-4');
    console.log('   状态:', textResult.success ? '✓ 成功' : '✗ 失败');
    if(textResult.success) {
      console.log('   内容长度:', textResult.result.length, '字符');
    } else {
      console.log('   错误:', textResult.error);
    }
  } catch (error) {
    console.log('   错误:', error.message);
  }
  
  // 测试3: 网络搜索
  console.log('\n3. 测试网络搜索功能...');
  try {
    const searchResult = await zhipuTools.webSearch('人工智能最新发展', 2);
    console.log('   状态:', searchResult.success ? '✓ 成功' : '✗ 失败');
    if(searchResult.success) {
      console.log('   结果数量:', Array.isArray(searchResult.result) ? searchResult.result.length : '未知');
    } else {
      console.log('   错误:', searchResult.error);
    }
  } catch (error) {
    console.log('   错误:', error.message);
  }
  
  console.log('\n快速测试完成！');
}

quickTest();