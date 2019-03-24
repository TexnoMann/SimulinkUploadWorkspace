# SimulinkUploadWorkspace

##Описание
Программа для выгрузки переменных из matlab файла и замены этих переменных на их значения в simulink модели.


## Установка
Используйте пакетный менеджер [pip3](https://pip.pypa.io/en/stable/) для установки всех необходимых пакетов.
```bash
git clone https://github.com/TexnoMann/SimulinkUploadWorkspace.git
```

```bash
pip3 install -r requirements.txt
```

## Запуск
Для запуска программы из под bash:
```bash
./uploader/modelVarChange.py  [-in|--input Путь до исходного .slx файла] [-out|--output Путь сохранения до выходного .slx файла] [-m|--mfile Путь до matlab файла с переменными для выгрузки]
```
## Примечание
Пограмма меняет переменные на их значения в slx для блоков "step, transfer func, constant, gain", а также в теле функций Matlab Function.

Внимание:
Не меняет значение переменных в аргументах функций и значение переменных, являющихся матрицами или другими структурами.

Пример с использованием абсолютного пути:
```bash
  ./uploader/modelVarChange.py -in /home/user/matlab/model.slx -out /home/user/matlab_val.slx -m /home/user/matlab_init.m
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
