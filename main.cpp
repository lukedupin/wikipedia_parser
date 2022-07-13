#include <QRegularExpression>
#include <QFile>
#include <QDir>
#include <QFileInfo>
#include <QIODevice>
#include <QList>
#include <QHash>
#include <QByteArray>

int main(int argc, char *argv[])
{
    if ( argc <= 1 ) {
        qDebug("Usage %s filename", argv[0]);
        return 0;
    }

    auto&& file = QFile( argv[1] );
    if ( !file.open(QFile::ReadOnly) ) {
        qDebug("Couldn't open %s", argv[1]);
        return 0;
    }

    const auto buffer_len = 0x800000;
    auto buffer = new char[buffer_len];
    auto size = 0;

    auto&& page = QRegularExpression("<page>");
    auto&& title_re = QRegularExpression("<title>(.*)</title>");
    auto&& username_re = QRegularExpression("<username>(.*)</username>");
    auto&& text_re = QRegularExpression("^.*<text[^>]+>");

    auto text = false;
    auto&& title = QString();
    auto&& username = QString();
    auto count = 0;

    QDir dir;
    QFile output;

    dir.mkdir("output");
    dir.setCurrent("output");

    //Read in the file
    while ( (size = file.readLine( buffer, buffer_len)) > 0 ) {
        auto line = QString::fromUtf8( buffer, size );

        if ( !text ) {
            QRegularExpressionMatch match;

            if ( page.match(line).hasMatch() ) {
                text = false;
                title = "";
                username = "";
            }
            else if ( (match = title_re.match(line)).hasMatch() ) {
                title = match.captured(1);
            }
            else if ( (match = username_re.match(line)).hasMatch() ) {
                username = match.captured(1);
            }
            else if ( text_re.match(line).hasMatch() ) {
                if ( title.isEmpty() ) {
                    qDebug("Invalid Title!!!");
                    continue;
                }
                if ( username.isEmpty() ) {
                    username = "Unknown";
                }

                dir.mkdir(username);

                auto&& filename = QString("%1/%2/%3.txt").arg(dir.currentPath()).arg(username).arg(title.replace('/', '_'));
                output.setFileName( filename );
                if ( !output.open(QIODevice::WriteOnly | QIODevice::Text) ) {
                    qDebug("Couldn't open file: %s -> %s", output.fileName().toUtf8().data(), output.errorString().toUtf8().data());
                    continue;
                }

                if ( (count & 255) == 0 ) {
                    qDebug("[%10d] Writing %s", count, QString("%1 -> %2").arg(username).arg(title).toUtf8().data());
                }

                //Remove the text line
                line = line.replace( text_re, "" );
                text = true;
            }

            //Did we start the text part of the content?
            if ( !text ) {
                continue;
            }
        }

        //Look for ending text
        if ( line.contains("</text>") ) {
            text = false;
            line = line.replace("</text>", "");

            count++;
            output.write( line.toUtf8());
            output.close();
        }
        else {
            output.write( line.toUtf8());
        }
    }

    return 0;
}
