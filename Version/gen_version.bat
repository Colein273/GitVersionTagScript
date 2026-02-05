go env -w GOOS=windows
go env -w GOARCH=amd64
go build -ldflags="-s -w" -o gen_version.exe gen_version.go
