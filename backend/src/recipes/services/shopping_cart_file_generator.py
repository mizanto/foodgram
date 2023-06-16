import csv
import io


class FileGeneratorFactory:
    @staticmethod
    def get_generator(format):
        if format == 'txt':
            return TextFileGenerator()
        elif format == 'csv':
            return CsvFileGenerator()
        else:
            raise ValueError(f'Unknown format: {format}')


class FileGenerator:
    def generate(self, content):
        raise NotImplementedError()


class TextFileGenerator(FileGenerator):
    def generate(self, ingredients):
        content = io.StringIO()
        content.write('Список покупок:')

        for name, data in ingredients.items():
            content.write(
                f'{name} - {data["amount"]} {data["measurement_unit"]}')

        content = content.getvalue()
        # content = 'Список покупок:\n\n'
        # for name, data in ingredients.items():
        #     content += f'{name} - {data["amount"]} \
        #         {data["measurement_unit"]}\n'
        return content, 'shopping_cart.txt', 'text/plain, charset=utf-8'


class CsvFileGenerator(FileGenerator):
    def generate(self, ingredients):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Ингредиент', 'Количество', 'Единица измерения'])
        for name, data in ingredients.items():
            writer.writerow([name, data["amount"], data["measurement_unit"]])
        return output.getvalue().encode('utf-8'), \
            'shopping_cart.csv', 'text/csv, charset=utf-8'
