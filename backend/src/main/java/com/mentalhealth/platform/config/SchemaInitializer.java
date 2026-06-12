package com.mentalhealth.platform.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class SchemaInitializer implements ApplicationRunner {
    private final JdbcTemplate jdbcTemplate;

    @Override
    public void run(ApplicationArguments args) {
        ensureCounselorProfileTable();
        ensureArticleTable();
        ensureNotificationTable();
        seedArticles();
        seedAssessmentScales();
    }

    private void ensureCounselorProfileTable() {
        jdbcTemplate.execute("""
            CREATE TABLE IF NOT EXISTS counselor_profile (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              user_id BIGINT NOT NULL,
              title VARCHAR(64),
              specialties VARCHAR(255),
              years_of_experience INT,
              introduction TEXT,
              price_per_hour DECIMAL(10, 2),
              online_status TINYINT DEFAULT 0,
              schedule_json TEXT,
              rating DECIMAL(3, 2) DEFAULT 5.00,
              review_count INT DEFAULT 0,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              deleted TINYINT DEFAULT 0
            )
            """);

        addColumnIfMissing("counselor_profile", "title", "ALTER TABLE counselor_profile ADD COLUMN title VARCHAR(64)");
        addColumnIfMissing("counselor_profile", "specialties", "ALTER TABLE counselor_profile ADD COLUMN specialties VARCHAR(255)");
        addColumnIfMissing("counselor_profile", "years_of_experience", "ALTER TABLE counselor_profile ADD COLUMN years_of_experience INT");
        addColumnIfMissing("counselor_profile", "introduction", "ALTER TABLE counselor_profile ADD COLUMN introduction TEXT");
        addColumnIfMissing("counselor_profile", "price_per_hour", "ALTER TABLE counselor_profile ADD COLUMN price_per_hour DECIMAL(10, 2)");
        addColumnIfMissing("counselor_profile", "online_status", "ALTER TABLE counselor_profile ADD COLUMN online_status TINYINT DEFAULT 0");
        addColumnIfMissing("counselor_profile", "schedule_json", "ALTER TABLE counselor_profile ADD COLUMN schedule_json TEXT");
        addColumnIfMissing("counselor_profile", "rating", "ALTER TABLE counselor_profile ADD COLUMN rating DECIMAL(3, 2) DEFAULT 5.00");
        addColumnIfMissing("counselor_profile", "review_count", "ALTER TABLE counselor_profile ADD COLUMN review_count INT DEFAULT 0");
        addColumnIfMissing("counselor_profile", "created_at", "ALTER TABLE counselor_profile ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP");
        addColumnIfMissing("counselor_profile", "updated_at", "ALTER TABLE counselor_profile ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP");
        addColumnIfMissing("counselor_profile", "deleted", "ALTER TABLE counselor_profile ADD COLUMN deleted TINYINT DEFAULT 0");
    }

    private void addColumnIfMissing(String tableName, String columnName, String alterSql) {
        Integer count = jdbcTemplate.queryForObject("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = ?
              AND column_name = ?
            """, Integer.class, tableName, columnName);

        if (count != null && count == 0) {
            log.info("Adding missing column {}.{}.", tableName, columnName);
            jdbcTemplate.execute(alterSql);
        }
    }

    private void ensureArticleTable() {
        jdbcTemplate.execute("""
            CREATE TABLE IF NOT EXISTS article (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              title VARCHAR(255) NOT NULL,
              category VARCHAR(64),
              summary TEXT,
              content LONGTEXT NOT NULL,
              author_name VARCHAR(64),
              status VARCHAR(32) DEFAULT 'PUBLISHED',
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              deleted TINYINT DEFAULT 0
            )
            """);
    }

    private void ensureNotificationTable() {
        jdbcTemplate.execute("""
            CREATE TABLE IF NOT EXISTS notification (
              id BIGINT PRIMARY KEY AUTO_INCREMENT,
              target_user_id BIGINT,
              target_role VARCHAR(32),
              title VARCHAR(255),
              content TEXT,
              created_by BIGINT,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              deleted TINYINT DEFAULT 0
            )
            """);
    }

    private void seedArticles() {
        upsertArticle(
            "睡不好？从“睡眠卫生”开始调整",
            "睡眠与放松",
            "规律作息、光线与屏幕习惯，往往比强迫自己睡着更有效。本文介绍可操作的睡眠卫生要点。",
            """
            为什么先谈睡眠卫生

            偶尔一两晚睡不好不必过度紧张，但若长期入睡困难、易醒或白天明显困倦，可以先把环境与习惯调整到更配合睡眠的状态。

            睡眠卫生不是药物，而是一组关于作息、环境与行为的日常策略，适合作为自我调节的起点。

            你可以尝试的具体做法

            尽量固定起床时间，即使前一晚睡得少，也避免白天长时间补觉，以免打乱节律。

            睡前一小时减少强光与刺激性内容；若必须用手机，可开启护眼模式并降低亮度。

            卧室以暗、静、凉为原则；床尽量只用来睡觉，减少在床上工作或刷剧。
            """,
            "平台内容组"
        );

        upsertArticle(
            "焦虑时，身体会发生什么？",
            "认识困扰",
            "心跳加快、肌肉紧绷、肠胃不适。了解焦虑的生理机制，有助于减少二次恐惧。",
            """
            焦虑是一种生存反应

            面对威胁时，身体会进入战斗或逃跑模式：交感神经兴奋，心率与呼吸加快，血液更多流向大肌肉群。

            当没有真实危险、身体却长期处于高唤醒状态，就可能表现为慢性焦虑或惊恐发作样的不适。

            可以做的自我调节

            缓慢延长呼气有助于激活副交感神经。

            把注意力带回当下环境，帮助神经系统降温。若症状频繁干扰生活，建议做更系统的专业评估。
            """,
            "平台内容组"
        );

        upsertArticle(
            "情绪低落时，可以试试这几步",
            "情绪与压力",
            "情绪有起伏是正常的。这里整理一些温和、可执行的小步骤，帮助你度过难熬的几天。",
            """
            先照顾身体的基本盘

            在情绪低谷时，大脑容易把小事放大成做不到。可以把目标降到最小：喝一口水、吃一点东西、洗把脸、到窗边站两分钟。

            不必追求立刻好起来，而是今天多完成一件小事就算进步。

            减少孤立感

            若暂时不想倾诉，也可以给信任的人发一句今天有点累，或者参加低压力的线上或线下活动。

            若你发现自己完全回避社交超过两周，建议考虑专业支持。
            """,
            "平台内容组"
        );

        upsertArticle(
            "和身边人谈边界：温和而清晰",
            "人际与沟通",
            "边界不是冷漠，而是让关系可持续。如何用“我”开头表达需求，同时给对方台阶？",
            """
            什么是心理边界

            边界包括你愿意在时间上付出多少、哪些话题不想讨论、哪些行为让你不舒服。清晰边界能减少委屈与爆发式争吵。

            表达公式示例

            “我”陈述：描述事实、你的感受、具体请求。例如：你这周三次临时改时间，我会有点焦虑；下次能否提前一天告诉我？

            少用“你总是”“你从来不”，把注意力放在具体事件与影响上。
            """,
            "平台内容组"
        );

        upsertArticle(
            "高压学习或工作下，如何识别快要撑不住的信号",
            "情绪与压力",
            "疲惫、迟钝、拖延、易怒，往往不是你不努力，而是系统已经超载。越早识别，越容易调整。",
            """
            过载往往先体现在节律混乱

            如果你连续几周睡眠变浅、食欲波动、白天提不起精神，说明身心已经在高负荷运转。

            这些表现未必立刻达到疾病标准，但足够提示你需要减压和求助。

            从停止继续加码开始

            把当前任务按必须完成、可以延期、可以求助三类拆开，不再靠硬扛解决全部问题。

            给自己预留恢复时间，比继续透支更能提升长期效率。
            """,
            "平台内容组"
        );

        upsertArticle(
            "亲密关系吵架后，先修复情绪还是先讲道理？",
            "人际与沟通",
            "在关系冲突里，顺序比内容更重要。情绪未降下来时，任何道理都容易被理解成攻击。",
            """
            冲突中的大脑优先处理威胁

            当你已经委屈、愤怒或防御时，大脑很难同时处理复杂逻辑，因此争论常常越讲越偏。

            这时最优先的不是赢，而是先让关系回到可谈状态。

            修复的常见步骤

            先暂停十到二十分钟，让双方从高唤醒里退下来。

            再用“刚才那句话让我感到被忽视”这类表述讲感受，而不是直接给对方下判断。
            """,
            "平台内容组"
        );

        upsertArticle(
            "当朋友向你倾诉低落时，怎样回应更有帮助",
            "人际与沟通",
            "很多人出于好意急着给建议，但陪伴和接住情绪，往往比立刻解决问题更重要。",
            """
            先接住，而不是立刻分析

            可以先回应“听起来你这段时间真的很难熬”或者“谢谢你愿意告诉我这些”。

            被理解能降低孤独感，也更有助于对方继续表达真实状态。

            避免这些常见误区

            避免说“别想太多”“你应该积极一点”这类看似鼓励、实际容易让对方更自责的话。

            如果你察觉对方有明显风险，比如提到伤害自己，应该尽快建议专业求助，并协助联系家人或机构。
            """,
            "平台内容组"
        );

        upsertArticle(
            "总觉得很累，但检查又没问题？可能是心理能量被透支",
            "认识困扰",
            "长期疲惫、提不起劲，并不一定只是休息不够，也可能和持续压力、情绪消耗有关。",
            """
            为什么心理透支常被忽视

            很多人把疲惫理解成意志力不够，继续逼自己坚持，却忽略了长期高压、关系负担和睡眠不足会一起消耗心理能量。

            当这种状态持续存在时，身体检查可能没有明显异常，但主观感受已经非常难熬。

            可以从哪些方面观察自己

            如果你发现自己早上醒来就觉得累、原本能完成的事情拖很久、对娱乐和社交也提不起兴趣，可以先把它当作需要认真对待的信号。

            及时调整节奏、降低任务负荷，并评估是否需要专业支持，比继续硬撑更有效。
            """,
            "平台内容组"
        );

        upsertArticle(
            "考试前特别紧张，怎么让自己稳下来",
            "情绪与压力",
            "考试焦虑并不罕见。关键不是完全不紧张，而是把紧张控制在还能发挥的范围内。",
            """
            紧张本身不一定是坏事

            适度唤醒能帮助集中注意力，但当你已经出现脑子发空、心跳过快、手脚冰凉时，就需要先让身体降下来。

            稳定状态的几个办法

            考前把复习目标改成查漏补缺，而不是临时全盘重来。

            练习缓慢呼吸和固定节奏的自我提示，比如告诉自己先完成眼前这一题。

            如果你每逢考试都出现明显躯体反应，也可以考虑做一次系统评估，看看是否存在持续性焦虑问题。
            """,
            "平台内容组"
        );

        upsertArticle(
            "总想刷手机停不下来，可能不是自制力差",
            "睡眠与放松",
            "反复刷短视频、信息流和社交平台，很多时候是在用刺激覆盖疲惫、无聊和焦虑。",
            """
            为什么手机会越来越难放下

            当大脑已经疲惫时，短平快的信息更容易带来即时反馈，所以你会下意识继续刷下去。

            这并不一定说明你懒，而是说明当前调节方式高度依赖外部刺激。

            比直接戒掉更现实的做法

            先限定某些时间段不碰手机，比如睡前半小时和起床后前二十分钟。

            再给自己准备替代行为，如听舒缓音乐、简单拉伸或写一页随手记录，让大脑有机会慢下来。
            """,
            "平台内容组"
        );
    }

    private void upsertArticle(String title, String category, String summary, String content, String authorName) {
        Integer count = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM article WHERE title = ? AND deleted = 0",
            Integer.class,
            title
        );
        if (count != null && count > 0) {
            return;
        }
        jdbcTemplate.update(
            "INSERT INTO article (title, category, summary, content, author_name, status) VALUES (?, ?, ?, ?, ?, 'PUBLISHED')",
            title, category, summary, content.trim(), authorName
        );
    }

    private void seedAssessmentScales() {
        Integer tableCount = jdbcTemplate.queryForObject("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
              AND table_name = 'assessment_scale'
            """, Integer.class);
        if (tableCount == null || tableCount == 0) {
            return;
        }

        upsertAssessmentScale(
            "大学生心理健康风险筛查",
            "MHP_MENTAL_RISK",
            "基于 MHP 大学生数据集训练的心理健康风险筛查模型，仅使用非 PHQ/GAD/PSS 答案字段，避免用答案推答案。",
            """
            [
              {"id":"age","type":"select","title":"年龄段","description":"请选择与数据集一致的年龄段","options":[{"label":"Below 18","value":"Below 18"},{"label":"18-22","value":"18-22"},{"label":"23-26","value":"23-26"},{"label":"27-30","value":"27-30"},{"label":"Above 30","value":"Above 30"}]},
              {"id":"gender","type":"select","title":"性别","description":"请选择性别选项","options":[{"label":"Female","value":"Female"},{"label":"Male","value":"Male"},{"label":"Prefer not to say","value":"Prefer not to say"}]},
              {"id":"university","type":"select","title":"学校","description":"请选择学校","options":[{"label":"American International University Bangladesh (AIUB)","value":"American International University Bangladesh (AIUB)"},{"label":"BRAC University","value":"BRAC University"},{"label":"Bangladesh Agricultural University (BAU)","value":"Bangladesh Agricultural University (BAU)"},{"label":"Bangladesh University of Engineering and Technology (BUET)","value":"Bangladesh University of Engineering and Technology (BUET)"},{"label":"Daffodil University","value":"Daffodil University"},{"label":"Dhaka University (DU)","value":"Dhaka University (DU)"},{"label":"Dhaka University of Engineering and Technology (DUET)","value":"Dhaka University of Engineering and Technology (DUET)"},{"label":"East West University (EWU)","value":"East West University (EWU)"},{"label":"Independent University, Bangladesh (IUB)","value":"Independent University, Bangladesh (IUB)"},{"label":"Islamic University of Technology (IUT)","value":"Islamic University of Technology (IUT)"},{"label":"North South University (NSU)","value":"North South University (NSU)"},{"label":"Patuakhali Science and Technology University","value":"Patuakhali Science and Technology University"},{"label":"Rajshahi University (RU)","value":"Rajshahi University (RU)"},{"label":"Rajshahi University of Engineering and Technology (RUET)","value":"Rajshahi University of Engineering and Technology (RUET)"},{"label":"United International University (UIU)","value":"United International University (UIU)"}]},
              {"id":"department","type":"select","title":"院系方向","description":"请选择院系方向","options":[{"label":"Biological Sciences","value":"Biological Sciences"},{"label":"Business and Entrepreneurship Studies","value":"Business and Entrepreneurship Studies"},{"label":"Engineering - CS / CSE / CSC / Similar to CS","value":"Engineering - CS / CSE / CSC / Similar to CS"},{"label":"Engineering - Civil Engineering / Similar to CE","value":"Engineering - Civil Engineering / Similar to CE"},{"label":"Engineering - EEE/ ECE / Similar to EEE","value":"Engineering - EEE/ ECE / Similar to EEE"},{"label":"Engineering - Mechanical Engineering / Similar to ME","value":"Engineering - Mechanical Engineering / Similar to ME"},{"label":"Engineering - Other","value":"Engineering - Other"},{"label":"Environmental and Life Sciences","value":"Environmental and Life Sciences"},{"label":"Law and Human Rights","value":"Law and Human Rights"},{"label":"Liberal Arts and Social Sciences","value":"Liberal Arts and Social Sciences"},{"label":"Other","value":"Other"},{"label":"Pharmacy and Public Health","value":"Pharmacy and Public Health"}]},
              {"id":"academic_year","type":"select","title":"当前年级","description":"请选择当前年级","options":[{"label":"First Year or Equivalent","value":"First Year or Equivalent"},{"label":"Second Year or Equivalent","value":"Second Year or Equivalent"},{"label":"Third Year or Equivalent","value":"Third Year or Equivalent"},{"label":"Fourth Year or Equivalent","value":"Fourth Year or Equivalent"},{"label":"Other","value":"Other"}]},
              {"id":"current_cgpa","type":"select","title":"当前 CGPA","description":"请选择当前 CGPA 区间","options":[{"label":"Below 2.50","value":"Below 2.50"},{"label":"2.50 - 2.99","value":"2.50 - 2.99"},{"label":"3.00 - 3.39","value":"3.00 - 3.39"},{"label":"3.40 - 3.79","value":"3.40 - 3.79"},{"label":"3.80 - 4.00","value":"3.80 - 4.00"},{"label":"Other","value":"Other"}]},
              {"id":"waiver_or_scholarship","type":"select","title":"是否获得奖助学金","description":"请选择是否获得 waiver 或 scholarship","options":[{"label":"No","value":"No"},{"label":"Yes","value":"Yes"}]}
            ]
            """,
            """
            {"model":"MHP-CatBoost-Mental-Risk","target":"mental_risk","screening":"心理健康风险筛查","high":"较高风险","recommendation":"建议进一步咨询专业人员","leakage_guard":"excluded PHQ/GAD/PSS item, score, label and risk columns"}
            """
        );
    }

    private void upsertAssessmentScale(String name, String code, String description, String questionJson, String ruleJson) {
        jdbcTemplate.update(
            """
            INSERT INTO assessment_scale (name, code, description, question_json, rule_json, enabled)
            VALUES (?, ?, ?, ?, ?, 1)
            ON DUPLICATE KEY UPDATE
              name = VALUES(name),
              description = VALUES(description),
              question_json = VALUES(question_json),
              rule_json = VALUES(rule_json),
              enabled = VALUES(enabled)
            """,
            name, code, description, questionJson.trim(), ruleJson.trim()
        );
    }
}
