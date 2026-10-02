# تشغيل MAHER CONTENT BRAIN على Cloudflare — من الصفر

هذه النسخة مصممة للمسار المجاني أولًا. الواجهة لا ترى أي API key. كل الأسرار توضع في Cloudflare Secrets.

## الروابط

- GitHub: https://github.com/mahr18/automatic-creators
- Cloudflare Workers: https://dash.cloudflare.com/
- Workers & Pages: https://dash.cloudflare.com/?to=/:account/workers-and-pages
- Google AI Studio — API Keys: https://aistudio.google.com/apikey
- Gemini API docs: https://ai.google.dev/gemini-api/docs
- Gemini pricing/limits: https://ai.google.dev/gemini-api/docs/pricing
- Cloudflare D1 docs: https://developers.cloudflare.com/d1/
- Cloudflare Workflows docs: https://developers.cloudflare.com/workflows/
- Cloudflare Workers Builds: https://developers.cloudflare.com/workers/ci-cd/builds/
- OpenAI API keys: https://platform.openai.com/api-keys

## A) مفتاح Gemini

أنت أنشأت هذا بالفعل من Google AI Studio.

احتفظ به ولا ترسله داخل الدردشة ولا تضعه في GitHub.

سنضعه في Cloudflare باسم:

GEMINI_API_KEY

## B) رمز دخول العقل

هذا ليس API key.

افتح الواجهة بعد النشر واضغط "توليد رمز دخول"، أو استخدم أي سلسلة عشوائية طويلة لا تقل عن 32 حرفًا.

ضع نفس القيمة في Cloudflare Secret باسم:

BRAIN_ACCESS_TOKEN

## C) لا تحتاج YouTube API الآن

YouTube API اختياري في هذه النسخة. اترك:

YOUTUBE_API_KEY

غير موجودًا.

العقل سيعمل من دونها. إذا قررت إضافتها لاحقًا، نفعّلها فقط لتحسين الإشارات العامة.

## D) لا تضع OpenAI الآن

OpenAI API مدفوع.

لذلك الكود الحالي يحميه افتراضيًا:

ENABLE_OPENAI_API=false

والـProvider:

AI_PROVIDER=gemini

معناه أن وجود OPENAI_API_KEY وحده لن يجعل النظام يستخدمه.

## E) إنشاء D1

يمكن تنفيذ هذا من جهاز فيه Node.js، أو من Cloudflare Dashboard.

من مجلد المشروع:

cd cloudflare

npx wrangler login

ثم:

npx wrangler d1 create maher-content-brain-db --binding DB --update-config

سيُضاف database_id الحقيقي إلى wrangler.jsonc تلقائيًا.

بعدها:

npx wrangler d1 execute maher-content-brain-db --remote --file=schema.sql

## F) أسرار Cloudflare

من Dashboard:

Workers & Pages → افتح Worker → Settings → Variables and Secrets → Add → Secret

أضف:

BRAIN_ACCESS_TOKEN = <نفس الرمز الذي ستستخدمه في الموقع>

GEMINI_API_KEY = <مفتاح Gemini الذي أنشأته>

ولا تضف OPENAI_API_KEY الآن.

يمكن بدل الواجهة استخدام Wrangler:

npx wrangler secret put BRAIN_ACCESS_TOKEN
npx wrangler secret put GEMINI_API_KEY

## G) إعداد Vars غير السرية

في Variables and Secrets أضف Variables:

AI_PROVIDER = gemini
GEMINI_TEXT_MODEL = gemini-3.8-flash
GEMINI_MAX_OUTPUT_TOKENS = 7000
GEMINI_DAILY_CALL_GUARD = 40
ENABLE_OPENAI_API = false
ENABLE_VIDEO_API = false

لا تضع API keys في Variables؛ استخدم Secret.

## H) النشر لأول مرة

من cloudflare:

npm install
npx wrangler types
npx wrangler deploy

بعدها Cloudflare سيعطيك رابط workers.dev.

افتح الرابط من iPhone.

## I) أول استخدام

1. افتح رابط Worker.
2. ضع BRAIN_ACCESS_TOKEN.
3. اختر AUTO.
4. اكتب طلبًا.
5. اضغط تشغيل العقل.
6. انتظر حتى يتحول إلى مكتمل.
7. ستظهر Production Pack + QA.
8. خذ Prompts المشاهد إلى أداة الفيديو التي تستخدمها في Google Flow/Veo.

لا تضع GEMINI_API_KEY أو OPENAI_API_KEY داخل الموقع.

## J) GitHub → Cloudflare بدون أوامر

بعد أن يعمل أول نشر، اربط GitHub من:

Cloudflare Dashboard → Workers & Pages → Create application → Import a repository

اختر:

mahr18/automatic-creators

وعند إعداد Build Root Directory استخدم:

cloudflare

ثم اربط الفرع main.

Cloudflare Workers Builds سيعيد النشر تلقائيًا مع كل push على الفرع المرتبط.

## K) لو تريد استخدام OpenAI لاحقًا

ضع:

OPENAI_API_KEY = <مفتاح OpenAI>

كـSecret.

ثم غيّر:

AI_PROVIDER = openai
ENABLE_OPENAI_API = true
OPENAI_MODEL = gpt-5.6-luna

لكن هذا ليس مسار $0. لا تفعّله أثناء التزامنا بالخطة المجانية.

## L) ماذا يفعل العقل الآن؟

طلب واحد يمر عبر 4 خطوات دائمة:

1. Research — يجمع إشارات عامة، الذاكرة، وYouTube إن كان API موجودًا.
2. Strategy + Production — Creative Director + Script + Storyboard + Prompt Compiler.
3. Critic + Repair — يفحص ويدخل في إصلاح فعلي بدل مجرد مدح.
4. Persist — يحفظ المهمة والفكرة والمصادر والذاكرة في D1.

والواجهة تستطلع حالة المهمة تلقائيًا، لذلك إغلاق شاشة المحادثة لا يجعل الطلب مربوطًا بطبقة HTTP طويلة.

## M) حدود مهمة

مجاني لا يعني بلا حدود. Gemini وCloudflare لديهما حدود استخدام، لذلك وضعنا Guard داخليًا.

GEMINI_DAILY_CALL_GUARD=40 يعني أن التطبيق نفسه يمنع أكثر من 40 استدعاء AI لذلك اليوم. هذا رقم أمان داخلي وليس حصة Google الرسمية.

Veo/video API غير مشغل ضمن المسار المجاني الافتراضي. السبب أن اشتراك Google AI الاستهلاكي لا يجب افتراض أنه يحول API video إلى API مجاني. استخدم Flow/Veo من واجهة اشتراكك للإنشاء المرئي عندما يكون ذلك متاحًا لك.

## N) فحص سريع بعد النشر

افتح:

/api/health

مع Bearer token للحصول على:
- provider
- model
- Gemini configured
- OpenAI enabled/disabled
- YouTube configured/optional
- app guard

ثم شغّل طلبًا قصيرًا قبل تجربة مشروع طويل.


## O) مراقبة المنافسين بدون YouTube API

يمكن تخزين Channel IDs عامة في:

POST /api/watchlist

مثال body:

{"channel_id":"UCxxxxxxxxxxxxxxxxxxxx","label":"Competitor A"}

العقل يقرأ آخر فيديوهات القنوات المحفوظة من YouTube RSS العام، لذلك لا تحتاج YOUTUBE_API_KEY لهذه الوظيفة.

لعرض القائمة:

GET /api/watchlist

## P) ذاكرة الأداء بدون YouTube Analytics API

يمكن حفظ أرقام من YouTube Studio يدويًا في:

POST /api/metrics

الحقول المدعومة:
video_id, title, published_at, impressions, views, ctr,
avg_view_duration_seconds, avg_percentage_viewed, likes, comments, notes

ثم يستخدم العقل آخر سجلات الأداء كذاكرة تاريخية في مرحلة البحث. لا يعتبرها بيانات لحظية من الإنترنت.

عرض السجلات:

GET /api/metrics

## Q) ماذا بقي خارج المسار المجاني

رفع الفيديو تلقائيًا إلى YouTube، توليد فيديوهات Veo عبر API، وتجميع MP4 سحابي طويل المدة تحتاج تكاملات أو موارد لا أريد تفعيلها تلقائيًا ضمن شرط $0.

لهذا النسخة الحالية تفصل:
Brain → Production Pack → Prompts
عن
Video generation → Assembly → Publishing

وهذا يسمح باستخدام Google Flow/Veo من واجهتك التي لديك، بينما يبقى العقل نفسه على المسار المجاني.
