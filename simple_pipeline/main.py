from simple_pipeline.core.simple_pipeline import SimplePipeline

if __name__ == '__main__':
    file_name = './example/pipeline_fuile_example.xml'
    pipeline = SimplePipeline(file_name)
    pipeline.run_pipeline()