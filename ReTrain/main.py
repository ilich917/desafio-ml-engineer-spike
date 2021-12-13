import set_logger
import preprocess.preprocesamiento as prep
import train_model.train as train_
set_logger.config()
prep.get_dataset()
train_.train()
