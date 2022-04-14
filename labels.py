# Inspired by https://github.com/mcordts/cityscapesScripts/helpers/labels.py


from collections import namedtuple

Label = namedtuple( 'Label' , [
    'name'        ,
    'id'          , 
    'category'    , 
    'categoryId'  , 
    'hasInstances',
    'ignoreInEval',
    'color'
    ] )


labels = [
    #       name                     id       category            catId     hasInstances   ignoreInEval   color
    Label(  'void'                 ,  0      , 'void'               , 0       , False        , True          , (  0,  0,  0) ),
    Label(  'dirt'                 ,  1      , 'drivable'           , 1       , False        , False         , (  108, 64, 20) ),
    Label(  'sand'                 ,  2      , 'drivable'           , 1       , False        , False         , (  255, 229, 204) ),
    Label(  'grass'                ,  3      , 'drivable'           , 1       , False        , False         , (  0, 102, 0) ),
    Label(  'tree'                 ,  4      , 'obstacle'           , 2       , False        , False         , (  0, 255, 0) ),
    Label(  'pole'                 ,  5      , 'obstacle'           , 2       , True         , False         , (  0, 153, 153) ),
    Label(  'water'                ,  6      , 'obstacle'           , 2       , False        , False         , (  0, 128, 255) ),
    Label(  'sky'                  ,  7      , 'sky'                , 3       , False        , False         , (  0, 0, 255) ),
    Label(  'vehicle'              ,  8      , 'vehicle'            , 4       , True         , False         , (  255, 255, 0) ),
    Label(  'generic-object'       ,  9      , 'object'             , 5       , False        , False         , (  255, 0, 127) ),
    Label(  'asphalt'              ,  10     , 'drivable'           , 1       , False        , False         , (  64, 64, 64) ),
    Label(  'gravel'               ,  11     , 'drivable'           , 1       , False        , False         , (  255, 128, 0) ),
    Label(  'building'             ,  12     , 'construction'       , 6       , False        , False         , (  255, 0, 0) ),
    Label(  'mulch'                ,  13     , 'drivable'           , 1       , False        , False         , (  153, 76, 0) ),
    Label(  'rock-bed'             ,  14     , 'obstacle'           , 2       , False        , False         , (  102, 102, 0) ),
    Label(  'log'                  ,  15     , 'obstacle'           , 2       , True         , False         , (  102, 0, 0) ),
    Label(  'bicycle'              ,  16     , 'vehicle'            , 4       , True         , False         , (  0, 255, 128) ),
    Label(  'person'               ,  17     , 'human'              , 7       , True         , False         , (  204, 153, 255) ),
    Label(  'fence'                ,  18     , 'obstacle'           , 2       , False        , False         , (  102, 0, 204) ),
    Label(  'bush'                 ,  19     , 'obstacle'           , 2       , False        , False         , (  255, 153, 204) ),
    Label(  'sign'                 ,  20     , 'object'             , 5       , False        , False         , (  0, 102, 102) ),
    Label(  'rock'                 ,  21     , 'obstacle'           , 2       , False        , False         , (  153, 204, 255) ),
    Label(  'bridge'               ,  22     , 'construction'       , 6       , False        , False         , (  102, 255, 255) ),
    Label(  'concrete'             ,  23     , 'drivable'           , 1       , False        , False         , (  101, 101, 11) ),
    Label(  'picnic-table'         ,  24     , 'object'             , 5       , True         , False         , (  114, 85, 47) ),
]

color2labels = { label.color: label for label in labels }
