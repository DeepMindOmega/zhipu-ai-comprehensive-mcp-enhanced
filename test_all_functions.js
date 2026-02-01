const ZhipuMCPTools = require('../clawd/skills/zhipu-mcp-tools/index.js');
const fs = require('fs');

async function testAllFunctions() {
  console.log('开始测试智谱AI MCP服务器的所有功能...\n');
  
  const zhipuTools = new ZhipuMCPTools();
  
  // 1. 测试网页分析功能
  console.log('1. 测试网页分析功能...');
  try {
    const webpageResult = await zhipuTools.analyzeWebpage('https://www.baidu.com');
    console.log('网页分析结果:', webpageResult);
  } catch (error) {
    console.log('网页分析出错:', error.message);
  }
  
  console.log('\n' + '='.repeat(50) + '\n');
  
  // 2. 测试联网搜索功能
  console.log('2. 测试联网搜索功能...');
  try {
    const searchResult = await zhipuTools.webSearch('人工智能发展趋势', 3);
    console.log('搜索结果:', searchResult);
  } catch (error) {
    console.log('搜索出错:', error.message);
  }
  
  console.log('\n' + '='.repeat(50) + '\n');
  
  // 3. 测试文本生成功能
  console.log('3. 测试文本生成功能...');
  try {
    const textResult = await zhipuTools.generateText('简要介绍人工智能的发展历程', 'glm-4');
    console.log('文本生成结果:', textResult);
  } catch (error) {
    console.log('文本生成出错:', error.message);
  }
  
  console.log('\n' + '='.repeat(50) + '\n');
  
  // 4. 测试仓库分析功能（如果可能的话）
  console.log('4. 测试仓库分析功能...');
  try {
    const repoResult = await zhipuTools.analyzeRepo('https://github.com/openai/openai-cookbook');
    console.log('仓库分析结果:', repoResult);
  } catch (error) {
    console.log('仓库分析出错:', error.message);
  }
  
  console.log('\n所有测试完成！');
}

testAllFunctions().catch(console.error);