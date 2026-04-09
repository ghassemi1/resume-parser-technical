from src.stages.postprocess import PostprocessStage
from src.pipeline import Context
text = open('out/resume_raw.txt','r',encoding='utf-8').read()
ctx = Context(input_path=None)
ctx.raw_text = text
ctx.result = {'email':'ghasemi1@gmail.com','phone':'581)-997-6463','skills':'Programming Python, R'}
stage = PostprocessStage()
stage.configure({'schema':'src/schema/resume_schema.json','fail_on_error':False})
stage.run(ctx)
print('name in result:', ctx.result.get('name'))
print('meta:', ctx.meta)
