curl -X POST http://localhost:1337/api/images/spatial_query/ \
     -H "Content-Type: application/json" \
     -d '{
           "geom": {
             "type": "Polygon",
             "coordinates":[[
                  [
                    105.62239681777376,
                    20.87882610031799
                  ],
                  [
                    106.04733609127125,
                    20.87882610031799
                  ],
                  [
                    106.04733609127125,
                    21.148023790045897
                  ],
                  [
                    105.62239681777376,
                    21.148023790045897
                  ],
                  [
                    105.62239681777376,
                    20.87882610031799
                  ]
              ]]
           },
           "operation": "intersects",
           "resolution_min": 0,
           "resolution_max": 2.0
         }'