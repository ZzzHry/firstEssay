// Authoring source; copy this file into build/ before running so bare imports
// resolve through the ignored runtime node_modules junction. No solver runs.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const here=path.dirname(fileURLToPath(import.meta.url));
const workspace=path.basename(here)==='build'?path.dirname(here):here;
const skill=process.env.PRESENTATIONS_SKILL_DIR || 'C:/Users/Hrychang/.codex/plugins/cache/openai-primary-runtime/presentations/26.1105.12137/skills/presentations';
const revision=process.env.DECK_REVISION || new Date().toISOString().replace(/[^0-9]/g,'');
const python=process.env.ARTIFACT_PYTHON || 'C:/Users/Hrychang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const FONT='Microsoft YaHei';
const C={navy:'#132D45',teal:'#007F80',orange:'#BB5B20',ink:'#193347',muted:'#516572',light:'#F0F5F7',grid:'#D5E0E5',white:'#FFFFFF'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
p.theme.defaultFont=FONT;
const slides=[];
const manifest=[];

function text(s,str,x,y,w,h,size=26,color=C.ink,bold=false,align='left'){
  const z=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  z.text=str;
  z.text.style={fontFamily:FONT,typeface:FONT,fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',insets:0,wrap:'word'};
  return z;
}
function rect(s,x,y,w,h,fill,line='none'){
  return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:line==='none'?0:1}});
}
function add(title,subtitle,notes,source='设计提案；尚未训练 RL'){
  const s=p.slides.add();s.background.fill=C.white;slides.push(s);
  text(s,title,58,35,1164,64,40,C.navy,true);
  if(subtitle)text(s,subtitle,60,110,1150,48,24,C.muted);
  rect(s,60,172,1160,2,C.teal);
  text(s,source,60,672,1090,28,16,C.muted);
  text(s,String(slides.length).padStart(2,'0'),1155,672,65,28,20,C.muted,false,'right');
  s.speakerNotes.text=notes;
  manifest.push({slide:slides.length,title,notes,source});
  return s;
}
function takeaway(s,str,y=608){text(s,str,60,y,1158,46,27,C.teal,true);}
function items(s,arr,x=60,y=210,w=1150,gap=88,size=28){
  arr.forEach((v,i)=>{text(s,String(i+1).padStart(2,'0'),x,y+i*gap,50,gap-10,25,C.teal,true);text(s,v,x+67,y+i*gap,w-67,gap-10,size);});
}
function table(s,headers,rows,widths,y=210,h=320,size=23){
  const values=[headers,...rows];
  const t=s.tables.add({rows:values.length,columns:headers.length,left:60,top:y,width:1160,height:h,columnWidths:widths,values});
  t.borders.assign({fill:C.white,width:1,style:'solid'});
  for(let i=0;i<values.length;i++)for(let j=0;j<headers.length;j++){
    const cell=t.getCell(i,j);cell.fill=i===0?C.navy:(i%2===1?C.light:C.white);
    cell.text.style={fontFamily:FONT,typeface:FONT,fontSize:i===0?size:size,color:i===0?C.white:C.ink,bold:i===0,insets:10,verticalAlignment:'middle'};
  }
  return t;
}
function chart(s,{title,categories,series,x=60,y=205,w=1160,h=360,max=60,unit='秒',legend=true,format='0.0'}){
  const ch=s.charts.add('bar',{position:{left:x,top:y,width:w,height:h},title,titleTextStyle:{fontSize:25,typeface:FONT,bold:true,fill:C.ink},categories,series,barOptions:{direction:'column',grouping:'clustered',gapWidth:100},hasLegend:legend,legend:{position:'bottom',overlay:false,textStyle:{fontSize:21,typeface:FONT,fill:C.ink}},xAxis:{textStyle:{fontSize:22,typeface:FONT,fill:C.ink},line:{fill:C.grid,width:1},majorGridlines:null},yAxis:{min:0,max,title:{text:unit,textStyle:{fontSize:20,typeface:FONT,fill:C.muted}},numberFormatCode:'0',textStyle:{fontSize:20,typeface:FONT,fill:C.muted},majorGridlines:{fill:C.grid,width:1}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:format,textStyle:{fontSize:21,typeface:FONT,fill:C.ink}},chartFill:C.white,chartLine:{fill:'none',width:0}});
  applyPresentationChartFont(ch,{fontFamily:FONT});return ch;
}

// 01 — Typographic cover, no invented results.
{
const s=p.slides.add();slides.push(s);s.background.fill=C.navy;
text(s,'ML-HRC-DLBP-CF · 组会研究设计',64,72,1150,50,28,'#97D9D5');
text(s,'面向整数最优证明的\n强化学习辅助整线列生成',64,196,1140,164,54,C.white,true);
text(s,'学习何时找列、如何投入；由精确内核核验方案与界',66,405,1145,64,30,'#DEE9ED');
text(s,'问题诊断 → 控制器设计 → 安全证明 → 验证计划',66,540,1145,48,26,'#97D9D5');
text(s,'2026.11.08   |   设计提案：已有候选策略试验，尚无 RL 训练结果',66,645,1130,35,20,'#DEE9ED');
const notes='开场先说明阶段：我们已经有整线分解算法与真实证书，也做过非学习候选策略试验。本次汇报是准备加入强化学习的设计，不展示不存在的训练效果。核心问题不是增加一个流行模块，而是让控制器在不同实例和不同求解状态下分配昂贵的定价投入。汇报约18–20分钟。代码阅读基线fb2b971d。详细设计见sub/agDetail/RL_DESIGN_NOTES_ZH.md。';s.speakerNotes.text=notes;manifest.push({slide:1,title:'面向整数最优证明的强化学习辅助整线列生成',notes,source:'研究设计，非已训练结果'});
}

{
const s=add('整线分解已建立优势，下一步改善求解效率','一列包含整条线的任务、站点、模式与资源配置。',
'先强调工作基础：这六例是论文已冻结的多线主实验，不能外推成所有大规模问题都优于Compact。整线列把线内AND、必拆、节拍、疲劳等纳入局部可行域，主问题只协调每线选列和共享人机资源。算法还包括受限IP恢复、按需资源档位查询和二维DP，不是只有根节点CG。参考sub/stage9/balanced_bound.py、demand_balanced.py；论文essay/myEssay/tables/formal.tex。600秒是协议总预算，Compact实际约595.7秒是预留持久化等预算后的观测时间，不能写成实测3600秒。',
'已有证据：论文 formal.tex；sub/stage12/evidence/formal600 证书');
table(s,['比较范围','整线分解框架','Compact CPLEX'],[['80任务 / 4线，3个seed','3/3 证明整数最优\n19.36–68.68 s','均未完成最优证明\n约 595.7 s'],['120任务 / 6线，3个seed','3/3 证明整数最优\n36.51–182.69 s','均未完成最优证明\n约 595.8 s']],[340,410,410],218,235,25);
text(s,'当前完整链：整线 CG → 整数恢复 → 必要时资源档位补全 / DP',60,498,1160,60,28);
takeaway(s,'目标：保持原模型与证明规则，减少得到好整数解和证书的代价。');
}

{
const s=add('真正的耗时集中在整线定价 PP','整线列降低组合冲突，也让单次局部 MILP 更困难。',
'图中PP时间是论文iterations.tex记录的原生优化时间，不包括全部Python或建模成本。总时间来自formal.tex，因此未归入PP的部分不能叫作RMP时间。六例PP/总时间约91.3%到98.7%，RMP原生优化均低于0.01秒。这说明当前最值得干预的是定价调用及其后续证明难度，而不是只优化很小的主问题。另一类资源紧实例还有31次档位查询的瓶颈，第一版控制器与档位后处理保持接口清晰。来源essay/myEssay/tables/iterations.tex、formal.tex；sub/agDetail/evidence_summary.json。',
'已有证据：iterations.tex、formal.tex；6例均为原生产框架');
chart(s,{title:'主实验 PP 原生求解时间',categories:['80/4/32','80/4/33','80/4/34','120/6/32','120/6/33','120/6/34'],series:[{name:'PP 原生秒',values:[17.67,22.79,66.70,34.24,102.94,180.31],fill:C.teal}],max:210,legend:false,y:205,h:330});
text(s,'PP 占总时间约 91%–99%    |    RMP 原生时间均 < 0.01 s',60,548,1160,45,28,C.orange,true);
takeaway(s,'RL 的价值要落到总时间和整数界，不能只落到“少了几轮”。');
}

{
const s=add('已有非学习试验：候选有得也有失，效果依赖实例','固定混合 fixed：候选价格 α=0.25；仍须原价认证。',
'这些图来自RL/adaptive_v1，不是完整生产balanced_bound：该实验没有资源档位DP，exact也带历史证明筛选。每配置只运行一次、60秒软算法预算，已看过的开发实例，不能作稳定泛化或统计显著性结论。左图两例都证明同样整数最优；右图seed34全部未证最优，exact实际43.7588秒、fixed55.0278秒；绝对Gap由124.4366到23.49。不能说RL已经取得81%的改进，因为没有RL网络，且算法耗时不同。fixed与手工adaptive该例只发生一次相同动作，结果相同不代表两个学习策略独立获胜。来源RL/adaptive_v1/RESULTS.md、SUMMARY.md、LIMITATIONS.md。',
'开发试验：每配置1次、60 s软预算；非 RL；无资源档位 DP');
chart(s,{title:'已证明最优：耗时 / s',categories:['80/4/s32','120/6/紧/s32'],series:[{name:'exact',values:[19.3542,29.8278],fill:C.navy},{name:'fixed',values:[51.5368,35.0962],fill:C.orange}],x:60,w:650,h:350,max:65});
chart(s,{title:'120/6/紧/s34：最终绝对 Gap',categories:['exact','fixed'],series:[{name:'Gap',values:[124.4366,23.49],points:[{idx:0,fill:C.navy},{idx:1,fill:C.orange}],fill:C.orange}],x:750,w:470,h:350,max:150,unit:'利润单位',legend:false});
text(s,'左图：固定候选更慢。右图：界改善，但两者均未证最优。',60,567,1160,40,26);
takeaway(s,'需要根据状态决定“尝不尝试”，不能默认每一轮都值得探索。');
}

{
const s=add('奖励设计必须避开已经观察到的误区','局部看起来更积极，不等于最终求解更有效。',
'80任务三种候选策略的认证轮数都从4降到3，但是全部比exact慢。fixed后续一次原价PP用了31.29秒，超过exact全部PP原生时间18.31秒。候选改变列池、对偶和CPLEX重优化状态，不能把损失全归结为候选额外的几秒。seed34 short_raw加11条候选列，fixed只加5条，但fixed的LB更高UB更低。当前观察支持研究长期序列决策，不证明RL必然优于可解释规则。所有数值见RL/adaptive_v1/SUMMARY.md、RESULTS.md。',
'已有证据：RL/adaptive_v1/SUMMARY.md、RESULTS.md');
table(s,['容易误用的指标','已经发生的反例','对设计的要求'],[['认证轮数更少','80任务：4轮 → 3轮\n但全部候选策略更慢','将后续认证耗时计入反馈'],['加入列更多','紧资源seed34：11列 vs 5列\n11列方案最终 Gap 更大','观察资源兼容性与整数界'],['候选求解很快','后续一次原价 PP：31.29 s\n超过 exact 全部 PP：18.31 s','评价整个后续轨迹']],[265,500,395],218,308,24);
takeaway(s,'主奖励：已验证整数解 + 有效 Gap + 时间；轮数和 RC 用于解释。');
}

{
const s=add('创新应落在控制目标和问题结构，不能只写“CG + RL”','已有 RL 选列、RL 定价，也已有拆卸线上的强化学习。',
'文献一Chi等NeurIPS2022用GNN支持序列选列；二Yuan等AAAI2024学习多列选择；三Abouelrous等2025预印本直接学习车辆路径定价，其摘要报告一定LP Gap下的效率，不应误写为整数精确证明；四Wang等Neurocomputing2024是导师要求引用的混合拆卸线SAC。我们拟研究共享资源兼容性观测和整数证明目标驱动的预算控制，但这些仍是假设，必须检索算法配置等邻近方向，不能声明首次。来源：[1] https://papers.neurips.cc/paper_files/paper/2022/hash/3ecfe5c632afb7d96a2337b18ff99b1f-Abstract-Conference.html [2] https://ojs.aaai.org/index.php/AAAI/article/download/28661/29284 [3] https://arxiv.org/abs/2504.02383 [4] https://doi.org/10.1016/j.neucom.2023.127145 。',
'定向文献核验：NeurIPS 2022；AAAI 2024；arXiv 2025；Neurocomputing 2024');
table(s,['研究方向','已有工作','本项目的拟研究差异'],[['RL 选列 [1,2]','选择一列 / 多列进入 RMP','控制昂贵定价的触发、价格和预算'],['RL 解定价 [3]','网络直接构造路线列','沿用原局部可行域和精确认证'],['RL 拆卸线 [4]','学习产品 / 任务分配','学习求解过程，面向整数界与证书']],[260,415,485],213,295,23);
text(s,'待验证的核心：资源兼容性观测 + 整数证明目标 + 序列预算控制',60,545,1160,48,27,C.teal,true);
text(s,'不宣称“首次 RL 列生成”；是否足够创新，取决于机制与消融证据。',60,608,1160,45,26,C.orange);
}

{
const s=add('第一版聚焦：候选定价与精确认证之间的控制','先缩小决策空间，复用已经验证的候选 / 认证接口。',
'第一版不直接改变原任务约束，也不训练任务逐个分配。直接构造整线方案会遇到复杂AND和疲劳约束，需要动作掩码与修复，工作量和风险都很高。RMP规模小也使通用列筛选的收益有限。现有接口已经允许短预算候选和强制认证，因此先学是否触发、价格混合和预算。资源档位选择值得单独开展第二阶段：选择哪个line,h,r精确查询，DP上下界不变，但本轮不和候选控制联合训练。相关代码RL/adaptive_v1/online.py；sub/stage9/demand_balanced.py。',
'设计选择；第一版只开放 Phase II 的候选控制');
table(s,['切入点','优点与代价','建议'],[['直接生成任务—站点—模式','动作维数大；需要复杂可行性修复','暂缓'],['选择已有列 / 压缩 RMP','已有成熟研究；当前 RMP 耗时很小','非当前优先'],['候选触发 + 价格 + 时间','接口已有；状态相关得失已有证据','第一版'],['资源档位查询选择','针对整数 Gap；需保留 DP 完整性','独立第二阶段']],[330,630,200],215,330,24);
takeaway(s,'只在可审计的控制层学习，完整的整线可行域保持不变。');
}

{
const s=add('控制器嵌入求解链：探索之后必须回到认证','学习模块提供动作；确定性模块负责可行性、有效界与终止。',
'从一个已可靠求解的RMP开始，读取现有对偶、列池、整数恢复和剩余预算。策略可直接CERTIFY，或启动受预算限制的候选。候选必须先核验原约束及原价RC；成功后重解RMP与受限IP，然后下一轮强制原价完整认证。无新列立即认证。若已验证LB与已有有效UB已经闭合，可安全直接结束。CG退出后生产版仍按同一确定性规则进行资源档位补全及DP。本流程不把候选截断或模型预测当成无改进列证明。实现参考RL/adaptive_v1/online.py的candidate/certification分离；资源后处理参考sub/stage9/demand_balanced.py。本图为计划接入完整生产链的结构，尚未实现学习控制器。');
const xs=[60,365,670,975],labels=['RMP + 整数恢复','RL 动作选择','候选找列 / 跳过','原价完整认证'];
xs.forEach((x,i)=>{rect(s,x,225,245,100,i===1?C.teal:C.light,i===1?'none':C.grid);text(s,labels[i],x+13,240,219,70,27,i===1?C.white:C.ink,true,'center');if(i<3)text(s,'→',x+255,240,40,70,38,C.teal,true,'center');});
text(s,'候选：验证局部可行性、利润和原价 RC → 加列后重解 RMP / IP',60,368,1160,60,28);
text(s,'认证：覆盖全部线路 → 修复有效 UB → 与已验证整数 LB 比较',60,445,1160,60,28);
text(s,'未闭合：继续既有 CG / 资源档位补全与 DP；超时保留真实状态',60,522,1160,60,28);
takeaway(s,'Phase I、原模型、档位 DP 和证书核验均保留。');
}

{
const s=add('状态：既看定价难度，也看整数组合的兼容性','所有特征来自当前和过去；没有最优答案或未来列。',
'资源档位就是一条线配置需要的人工数h与机器人数r。不同整线列可能都有高利润，但若资源需求高度集中，就难以跨线组合。观察已知列池的档位分布有助于区分找列收益。第一版不计算未知档位的真正最优利润，只用已有数据。LB/UB缺失必须有掩码；浮点异常要拒绝。各线使用共享编码器再池化，避免依赖任意线标签；静态特征可以从输入预计算。CPLEX内部warm state不可见，因此保留最近三轮历史，且将过程称为部分可观测。数据源sub阶段结果、RL/adaptive_v1日志；均为计划特征。');
table(s,['观测层','建议输入','与决策的联系'],[['全局进展','剩余预算、有效 LB/UB、Gap、停滞','是否值得花时间探索'],['价格与定价','对偶变化、最近 PP 时间 / 状态 / RC','原价认证是否困难'],['每线结构','任务 / 站点、AND密度、模式与疲劳统计','整线局部难度'],['资源兼容性','已知 (h,r) 档位分布、受限 IP witness','候选能否改善整数组合'],['历史与掩码','最近3轮动作；缺失界 / 结果标志','处理延迟影响和不可见状态']],[235,580,345],210,350,23);
takeaway(s,'禁止输入测试最优值、未来列和实例生成器的构造 witness。');
}

{
const s=add('动作：一个直接认证选项，六种候选投入','7 个离散动作，先控制规模，不直接输出任务分配。',
'价格混合使用当前原价和过去完整认证中有效修复UB最好的参考价格。没有历史参考时用零，这与现有开发接口一致。alpha等于1就是短预算原价候选，不能误以为自动精确；0.5与0.25对价格作不同强度混合。tau是每条线native候选时间，L条线意味着大约L*tau，再加建模验证开销，因此动作掩码需要按全局剩余预算检查。候选总预算初始上限20%，预留认证和写盘空间。所有数字是实验起点，还没有调参证明。sigma_l只在目标里提供常数，但RC核验不能漏掉。');
text(s,'候选价格：π̃ = α π当前 + (1 − α) π历史认证',60,205,1160,60,32,C.teal,true);
table(s,['动作','价格 α','每线候选预算 τ','之后的必经步骤'],[['CERTIFY','当前原价','不花候选预算','完整原价精确定价'],['候选 1–2','1.00','0.5 / 2 s','验列 → RMP/IP → 强制认证'],['候选 3–4','0.50','0.5 / 2 s','验列 → RMP/IP → 强制认证'],['候选 5–6','0.25','0.5 / 2 s','验列 → RMP/IP → 强制认证']],[225,180,250,505],285,267,23);
takeaway(s,'候选软预算目标 20%；预留认证与写盘；不足时只允许认证。');
}

{
const s=add('证书不交给网络：上界来自完整定价，下界来自真方案','即使策略选得不好，也只能更慢或超时，不能产生虚假的证明。',
'最大化形式下共享资源对偶非负，凸性对偶自由。rho_l为原价下全列最大检验数，必须获可靠证明。将每个凸性对偶增加max(0,rho_l)构造全列对偶可行解，从而得到UB。D_RMP是经核验的对偶目标，强对偶下等于RMP primal。每线误差累积，不能把epsilon_rc直接叫总体误差。整数LB来自数据级原约束核验。混合价格候选、最大化PP incumbent以及超时无列都不能代替rho。若候选控制导致未证认证，保留有效历史界并按旧安全策略终止/后处理。有限预算不保证任何实例都证完；证明可靠性与完成率必须区分。',
'数学内核：原价 RC、完整块覆盖、原约束 witness、原数值容差');
text(s,'原价检验数：rcₗₚ = cₗₚ − πᴴ hₗₚ − πᴿ rₗₚ − σₗ',60,210,1160,75,31,C.navy,true);
text(s,'有效上界：UB = D_RMP + Σₗ max(0, ρₗ)',60,309,1160,70,33,C.teal,true);
items(s,['全部线路的原价定价有证据，才允许更新完整 LP 认证界。','整数 LB 必须通过任务、优先、资源、疲劳等原约束检查。','只有有效 UB 与已验证 LB 闭合，才能声明整数最优。'],60,409,1160,58,25);
takeaway(s,'候选列合法 ≠ PP 已证最优 ≠ 原整数问题已证最优。');
}

{
const s=add('训练过程：反馈应覆盖候选引发的后续代价','把一次动作视为持续时间可变的宏动作。',
'当前试验已经看到候选之后的原价求解变难，所以即时奖励最大RC可能方向错误。宏动作至少包括候选、重解RMP/IP和强制认证；其对未来轮与档位补全的影响由episode回报反映。原生求解时间不同，过程更接近SMDP且部分可观测。训练若只保留根CG，结论也只能是根CG；正式环境必须接入相同确定性档位DP，并纳入终止回报。JSON重放不包含CPLEX内部warm state，不能把重放视作完全等价的可克隆状态。数据采集应执行完整真实轨迹。');
table(s,['层级','包含的过程','反馈内容'],[['一次决策','观察状态 → 选动作','动作概率、掩码、剩余预算'],['一个宏动作','候选或跳过 → RMP/IP → 强制认证','真实耗时、有效界、整数 witness'],['整个 episode','重复控制 → 同一档位补全 → 持久化','终端 Gap、整数证明、总时间']],[240,575,345],218,280,24);
text(s,'状态并非完全可观测：候选会改变 CPLEX 后续重优化状态。',60,535,1160,55,28,C.orange);
takeaway(s,'先保留近期历史；不要把“同一对偶”误认为“同一求解状态”。');
}

{
const s=add('奖励：少等待、早有整数解、缩小有效 Gap','用整个预算中的有效界轨迹评价策略。',
'建议定义从输入得到的固定正利润尺度S，不能用最终最优值归一化。有效有限LBUB都存在时g=min(1,(UB-LB)/S)，否则g=1并保留缺失掩码。UB低于LB超过容差时是错误，不能通过max截成零掩盖。奖励积分由验证完成的事件更新。示例权重仅为起点：time=.05，gap=1，无解=.25，终止证书bonus=.2。有限回合可先用gamma=1，因为真实时间已在奖励中；若再按步折扣会偏向求解步数。完整不可行证书可获得终止奖励，但未找到整数解不能叫不可行。未证提前停机时，用最后有效Gap和整数解状态补计到总预算T，不能奖励提前放弃；无需真的等待。实际时间项只计真实耗时。评价中仍单独报告真实Gap与时间，不让复合奖励替代科研指标。');
text(s,'rₜ = −(1/T) ∫ [ w时间 + wGap · g(u) + w无解 · I(无整数解) ] du',60,208,1160,76,28,C.navy,true);
text(s,'       + b证明 · I(首次获得完整终止证书)',60,288,1160,54,28,C.teal,true);
text(s,'g(u)：按输入利润尺度归一化的有效 Gap；缺少可靠界时记为 1。',60,342,1160,34,23,C.muted);
table(s,['奖励项','为什么需要','实现边界'],[['有效 Gap 面积','同样终点，越早改善越好','缺界设掩码；不使用事后最优值'],['没有整数解的时间','高 LP 值不能替代可执行方案','只认原约束验证通过的 witness'],['时间与完成证书','约束候选开销，鼓励完成证明','未证提前停机：补计剩余 Gap']],[275,420,465],378,197,23);
takeaway(s,'奖励权重在验证集确定；轮数、列数和 RC 不作主奖励。');
}

{
const s=add('网络先做小：共享编码器 + 动作掩码 + PPO','先回答序列学习是否有价值，再考虑更复杂的图网络。',
'计划每条线的静态和动态特征送入共享两层64维MLP，mean和max池化与全局特征拼接，actor输出7个动作，critic输出价值。最近三轮历史先拼接，必要时再试GRU，不需要立刻构造很大的任务图GNN。PPO仅是成熟训练算法，不构成创新。与相同动作空间的contextual bandit比较：如果只看当前状态即可选好动作，bandit应优先。旧日志是其他策略采集的，不能当作PPO当前策略on-policy轨迹直接训练；可用于预热或观察分析。PPO文献Schulman et al. 2017 https://arxiv.org/abs/1707.06347。');
items(s,['每线共享小 MLP（建议 2×64）→ mean/max pooling → 全局特征。','Actor 输出 7 个动作；无效预算动作屏蔽；Critic 估计后续回报。','先用真实求解轨迹训练 PPO；旧日志仅用于调试、分析或预热。','同时训练同动作空间的上下文老虎机，检验长期决策是否必要。'],60,212,1160,88,28);
takeaway(s,'若 bandit 或固定规则同样好，应选择更简单、训练成本更低的方法。');
}

{
const s=add('数据划分：按完整产品 / 任务库隔离','已观察的 seed32 / seed34 只做开发，不再冒充未见测试。',
'仅按随机种子字符串划分不够：同一基础任务库派生不同线数、资源比例的输入也可能泄漏。因此按原始产品任务库或生成族分组。输入一次生成并冻结字节和SHA，各方法共用，不将构造见证作为MIP start给某个方法。先用30个新开发实例检查动作互补，正式测试至少20到30独立实例和3个训练种子只是起点，实际应依据方差和计算成本调整。OOD要分别考察线数和每线任务数：增加总任务但每线不变，不能替代单线定价难度泛化。测试前冻结权重和参数。所有样本规模均为计划，尚未执行。');
table(s,['集合','用途','必须隔离'],[['训练','新轨迹与策略更新','不读取验证 / 测试最终解'],['验证','动作参数、奖励权重、早停','不反复挑选测试实例'],['最终测试','整数质量、证明率、总时间','同一任务库不得跨集合'],['OOD 测试','更多线路 / 每线更多任务 / 更紧资源','分别报告各维度退化']],[200,435,525],213,315,24);
text(s,'起步建议：30个新开发例 → 通过安全回归 → 再扩大训练与独立测试',60,555,1160,49,26);
takeaway(s,'冻结输入 JSON / SHA、求解器配置、预算与数值容差。');
}

{
const s=add('比较对象必须足够强，预算必须覆盖整个求解过程','先证明控制器有价值，再与 Compact 比较最终算法。',
'第一层是相同新引擎关闭候选，与完整生产balanced_bound对齐证明和结果。第二层所有控制器使用相同动作空间、缓存设置、warm start、档位后处理和预算。固定混合不是唯一强基线，还应有确定性价格稳定化和预算规则。第三层才是锁定算法与Compact的论文级比较。指标需要真实整数LB、有效UB/Gap、首个整数解、证明完成率、端到端时间、Gap曲线面积；超时按预算删失而不写成未运行的3600秒。报告训练成本和推理开销，训练种子不能充当更多独立实例。');
table(s,['对照层','方法','主评价'],[['正确性对齐','生产框架；新引擎 exact 模式','原模型结果、证书、整数界'],['控制机制','short_raw / fixed / 手工规则\n稳定化规则 / bandit / PPO','有效 Gap、证明时间、胜平负'],['论文最终算法','冻结后的 RL 框架 vs Compact','同总预算 LB / UB / 证明率']],[225,565,370],218,275,24);
text(s,'同机器、单线程、相同输入 / solver seed；计入推理、验证和持久化。',60,533,1160,58,27);
takeaway(s,'保留失败与退化实例；不以“迭代更少”替代“端到端更有效”。');
}

{
const s=add('消融与故障注入：同时解释收益、检验证明边界','控制器可以不聪明，但不能绕过数学核验。',
'消融不仅比较有无RL，还要隔离触发、价格和时间预算三种作用，再比较资源兼容性特征和整数奖励。bandit和PPO判断长期收益。相同列池对偶的微基准说明接口成本，完整轨迹比较说明搜索轨迹影响，二者不能混用。安全测试沿用原独立枚举Oracle与证书重放，并新增动作接口所有分支的故障注入。旧RL/adaptive_v1已经有29份正常证书及故障拒绝基础，这不是新RL模块通过测试，必须接入后重新执行。旧回归范围见其SUMMARY。');
table(s,['机制消融','安全回归'],[['仅学触发 → 再加价格 → 再加预算','小例完整列 Oracle / 原价 RC 独立核验'],['有无资源兼容性特征','整数 witness / Phase I / 全线路认证覆盖'],['整数奖励 vs 只看 LP','候选冒充证明 / 过期对偶 / 未来参考'],['bandit vs PPO；无历史 vs 有历史','定价截断 / 异常状态 / 错误上界拒绝'],['同前缀微基准 + 完整轨迹对照','新证书重放；所有动作共用证明内核']],[580,580],214,350,24);
takeaway(s,'先通过独立安全验证，再扩大训练和性能实验。');
}

{
const s=add('落地分四步，每一步都有停止条件','本轮完成设计；后续只在证据支持时增加复杂度。',
'步骤一冻结开发接口和旧数据，加入观察与预算记录，先让关闭候选的新环境和完整生产链对齐。步骤二用新实例测试动作互补，并比较规则和bandit，如果控制层没有可重复收益就停止扩大RL。步骤三少动作小网络PPO，完整安全回归后再扩大。步骤四锁定模型和协议，做独立测试和消融，然后Compact比较。候选预算用尽或单个原价PP依旧决定全部成本时，主痛点可能不在策略，应该转原生定价或资源档位调度。此路线不承诺多少天或必然加速。');
table(s,['阶段','实际工作','进入下一步的门槛'],[['1 环境对齐','接候选控制与生产档位后处理\n补观察、动作、完整预算日志','exact 结果与证书一致'],['2 动作价值','新实例；规则 / bandit\n分析资源紧与 PP 困难场景','互补收益超过控制开销'],['3 小规模 RL','小网络 PPO；独立划分\n所有动作的安全回归','优于强规则且证书全通过'],['4 最终验证','多训练种子、独立测试、消融\n冻结算法后与 Compact 比较','可重复的整数效果 / 证明效率']],[210,585,365],215,342,23);
takeaway(s,'若控制收益不足：优先改进原生 PP 或档位补全，不盲目扩网络。');
}

{
const s=add('今晚可以提出的三个研究假设','这些是要检验的问题，不是已经得到的结论。',
'收束时明确假设：第一，资源兼容性与定价难度联合观测能预测候选是否值得投入；第二，整数界与时间奖励优于只奖RC和轮数；第三，候选的长期轨迹影响足够强，PPO优于同动作bandit。安全内核使性能退化不变成错误证明，但不保证所有实例都在预算内完成。下一步先新开发例和规则基线，避免今晚给导师展示成已经实现RL创新。对于创新性批评，应承认现有分解加通用RL不够，真正贡献需要上述机制和独立证据。');
items(s,['资源感知：已知 (h,r) 档位与整数恢复状态，能帮助选择候选投入。','目标对齐：整数 Gap 与时间奖励，能改善可执行方案和证明效率。','长期决策：策略能预见候选对后续认证的影响，优于同动作 bandit。'],60,218,1160,114,29);
text(s,'已完成：精确框架 + 非学习候选试验 + 本次设计。\n待完成：训练环境对齐、RL 训练、泛化和公平性能验证。',60,559,1160,90,27,C.teal,true);
}

{
const s=add('参考文献与本地证据入口','完整链接、逐页讲解与适用边界已写入演讲者备注。',
'学术来源核验于2026-11-08，均使用作者论文或会议/出版社原始来源。[1] Chi et al. NeurIPS2022 https://papers.neurips.cc/paper_files/paper/2022/hash/3ecfe5c632afb7d96a2337b18ff99b1f-Abstract-Conference.html 。[2] Yuan et al. AAAI2024 https://ojs.aaai.org/index.php/AAAI/article/download/28661/29284 DOI10.1609/aaai.v38i8.28661 。[3] Abouelrous et al.2025 https://arxiv.org/abs/2504.02383 （预印本）。[4] Wang et al.Neurocomputing2024 https://www.sciencedirect.com/science/article/pii/S0925231223012687 DOI10.1016/j.neucom.2023.127145 。[5] Schulman et al.2017 https://arxiv.org/abs/1707.06347 。本地证据essay/myEssay/tables/formal.tex、iterations.tex，RL/adaptive_v1/RESULTS.md、SUMMARY.md、LIMITATIONS.md，RL/reuse_v1/SUMMARY.md，sub/agDetail/evidence_summary.json。源码RL/adaptive_v1/online.py与sub/stage9/balanced_bound.py、demand_balanced.py。本次没有新solver性能运行，也没有RL训练。',
'本次仅生成设计与汇报材料；不修改算法，不改写已封存实验');
const refs=[
'[1] Chi et al.  A Deep Reinforcement Learning Framework for Column Generation. NeurIPS, 2022.',
'[2] Yuan et al.  A Reinforcement-Learning-Based Multiple-Column Selection Strategy for Column Generation. AAAI, 2024.',
'[3] Abouelrous et al.  Reinforcement Learning for Solving the Pricing Problem in Column Generation. arXiv:2504.02383, 2025.',
'[4] Wang et al.  Reinforcement learning for Hybrid Disassembly Line Balancing Problems. Neurocomputing 569:127145, 2024.',
'[5] Schulman et al.  Proximal Policy Optimization Algorithms. arXiv:1707.06347, 2017.'
];refs.forEach((r,i)=>text(s,r,60,208+i*72,1160,66,22));
text(s,'本地：ALGORITHM_DESIGN_ZH.md / RL_DESIGN_NOTES_ZH.md / RL/adaptive_v1/',60,596,1160,55,24,C.teal,true);
}

await fs.mkdir(path.join(workspace,'build'),{recursive:true});
await fs.mkdir(path.join(workspace,'previews'),{recursive:true});
await fs.mkdir(path.join(workspace,'output'),{recursive:true});
await fs.writeFile(path.join(workspace,'slide_manifest.json'),JSON.stringify(manifest,null,2)+'\n','utf8');
const draft=path.join(workspace,'build','candidate-'+revision+'.pptx');
await (await PresentationFile.exportPptx(p)).save(draft);
console.log('Draft exported: '+draft);
const final=path.join(workspace,'output','RL_DESIGN_GROUP_MEETING_20261108_'+revision+'.pptx');
const result=await finalizePresentation({workspaceDir:workspace,candidatePath:draft,finalPath:final,pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[2,5,6,7,9,10,12,13,15,16,17,18].flatMap(n=>['--require-native-table-slide',String(n)])],materializeLiteralChartWorkbooks:true,requiredNativeTableOwnerSlides:[2,5,6,7,9,10,12,13,15,16,17,18],requiredNativeChartOwnerSlides:[3,4],fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(workspace,'build','validation-'+revision+'.json')});
console.log('Finalized '+JSON.stringify(result));
for(let i=0;i<slides.length;i++){
  const blob=await p.export({slide:slides[i],format:'png',scale:1});
  await fs.writeFile(path.join(workspace,'previews',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
  console.log('Rendered '+(i+1));
}
await fs.copyFile(final,path.join(workspace,'..','RL_DESIGN_GROUP_MEETING_20261108.pptx'));
console.log('Delivered final PPTX under sub/agDetail');
