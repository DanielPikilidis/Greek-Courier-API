package main

type TrackingError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

type Data struct {
	Success bool               `json:"success"`
	Data    map[string]Package `json:"data"`
	Error   TrackingError      `json:"error"`
}

// func (d *Data) Unmarshal(data []byte) error {
// 	d.Data = make(map[string]Package)
// 	return jsoniter.Unmarshal(data, &d)
// }

type Package struct {
	Found        bool       `json:"found"`
	Courier_name string     `json:"courier_name"`
	Courier_icon string     `json:"courier_icon"`
	Locations    []Location `json:"locations"`
	Delivered    bool       `json:"delivered"`
}

type Location struct {
	Datetime    string `json:"datetime"`
	Location    string `json:"location"`
	Description string `json:"description"`
}
