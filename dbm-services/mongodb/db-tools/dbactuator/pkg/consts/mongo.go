package consts

import (
	"dbm-services/mongodb/db-tools/dbmon/pkg/consts"
	"dbm-services/mongodb/db-tools/mongo-toolkit-go/pkg/mymongo"
	"fmt"
	"path"
	"time"

	"github.com/pkg/errors"
)

// MongoVersionV24 TODO
const MongoVersionV24 = "2.4"

// MongoVersionV30 TODO
const MongoVersionV30 = "3.0"

// MongoVersionV32 TODO
const MongoVersionV32 = "3.2"

// MongoVersionV34 TODO
const MongoVersionV34 = "3.4"

// MongoVersionV36 TODO
const MongoVersionV36 = "3.6"

// MongoVersionV40 TODO
const MongoVersionV40 = "4.0"

// MongoVersionV42 TODO
const MongoVersionV42 = "4.2"

// MongoVersionV100 TODO
const MongoVersionV100 = "100.7" // >= 4.4 https://www.mongodb.com/docs/database-tools/
// MongoInstallDir TODO
const MongoInstallDir = "/usr/local/mongodb"

// GetMongodumpBin 根据版本号获取mongodump的二进制文件名
// 2.x : 不支持
// 3.x, 4.0, 4.2: mongodump.$v0.$v1
// others: mongodump.100
func GetMongodumpBin(version *mymongo.MongoVersion) (bin string, err error) {
	if version == nil {
		return "", errors.New("version is nil")
	}

	switch version.Major {
	case 2:
		return "", fmt.Errorf("not support version:%s", version.Version)
	case 3:
		bin = fmt.Sprintf("mongodump.%d.%d", version.Major, version.Minor)
	case 4:
		switch version.Minor {
		case 0, 2:
			bin = fmt.Sprintf("mongodump.%d.%d", version.Major, version.Minor)
		}
	default:
		bin = fmt.Sprintf("mongodump.%s", MongoVersionV100) // 100.7

	}
	bin = path.Join(consts.GetDbToolDir(""), "mongotools", bin)
	return
}

// GetMongorestoreBin 根据版本号获取mongodump的二进制文件名
// 2.x : 不支持
// others: mongodump.100
func GetMongorestoreBin(version *mymongo.MongoVersion) (bin string, err error) {
	if version == nil {
		return "", errors.New("version is nil")
	}

	switch version.Major {
	case 2:
		return "", fmt.Errorf("not support version:%s", version.Version)
	default:
		bin = fmt.Sprintf("mongorestore.%s", MongoVersionV100) // 100.7

	}
	bin = path.Join(consts.GetDbToolDir(""), "mongotools", bin)
	return
}

// GetMongoShellBin 根据版本号获取mongodump的二进制文件名
// 2.x : 不支持
// others: mongodump.100
func GetMongoShellBin(version *mymongo.MongoVersion) (bin string, err error) {
	if version == nil {
		return "", errors.New("version is nil")
	}
	if version.Major >= 6 {
		bin = "mongosh"
	} else {
		bin = "mongo"
	}

	bin = path.Join(MongoInstallDir, "bin", bin)
	return
}

// GetMongoBackupReportPath 获取上报目录 /home/mysql/dbareport/mongo/backup/backup-%Y%m%d.log
func GetMongoBackupReportPath() (string, string, string) {
	return GetMongoReportPath("backup")
}

// GetMongoReportPath 获取上报目录 /home/mysql/dbareport/{dbName}/{reportType}/{reportType}-%Y%m%d.log
func GetMongoReportPath(reportType string) (string, string, string) {
	dirName := path.Join(DbaReportSaveDir, "mongo", reportType)
	today := time.Now().Local().Format("20060102")
	fileName := fmt.Sprintf("%s-%s.log", reportType, today)
	return path.Join(dirName, fileName), dirName, fileName
}
