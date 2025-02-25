package api

import (
	"encoding/json"
	"net/http"
	"net/url"
	"strings"
	"time"

	"dbm-services/mysql/db-tools/mysql-crond/pkg/config"

	"github.com/pkg/errors"
)

// SimpleEntry TODO
type SimpleEntry struct {
	ID   int                `json:"ID"`
	Job  config.ExternalJob `json:"Job"`
	Next time.Time          `json:"NextTime"`
}

// Entries entries list
func (m *Manager) Entries() ([]*SimpleEntry, error) {
	resp, err := m.do("/entries", http.MethodGet, nil)
	if err != nil {
		return nil, errors.Wrapf(err, "manager call %s", m.apiUrl)
	}

	var res struct {
		Entries []*SimpleEntry `json:"entries"`
	}
	err = json.Unmarshal(resp, &res)
	if err != nil {
		return nil, errors.Wrapf(err, "manager unmarshal %s response", m.apiUrl)
	}

	return res.Entries, nil
}

// EntriesWithParam TODO
func (m *Manager) EntriesWithParam(param url.Values) ([]*SimpleEntry, error) {
	resp, err := m.do("/entries", http.MethodGet, param)
	if err != nil {
		return nil, errors.Wrapf(err, "manager call %s", m.apiUrl)
	}

	var res struct {
		Entries []*SimpleEntry `json:"entries"`
	}
	err = json.Unmarshal(resp, &res)
	if err != nil {
		return nil, errors.Wrapf(err, "manager unmarshal %s response", m.apiUrl)
	}

	return res.Entries, nil
}

// SimpleEntryList 用于自定义排序
type SimpleEntryList []*SimpleEntry

// Len 用于排序
func (e SimpleEntryList) Len() int {
	return len(e)
}

// Less 用于排序
func (e SimpleEntryList) Less(i, j int) bool {
	if e[i].Job.Command > e[j].Job.Command {
		return true
	} else if e[i].Job.Command == e[j].Job.Command && e[i].Job.Schedule > e[j].Job.Schedule {
		return true
	} else if e[i].Job.Command == e[j].Job.Command && e[i].Job.Schedule == e[j].Job.Schedule &&
		strings.Join(e[i].Job.Args, " ") > strings.Join(e[j].Job.Args, " ") {
		return true
	}
	return false
}

// Swap 用于排序
func (e SimpleEntryList) Swap(i, j int) {
	e[i], e[j] = e[j], e[i]
}
