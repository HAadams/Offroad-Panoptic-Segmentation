# Inspired by https://github.com/mcordts/cityscapesScripts/helpers/labels.py


from collections import namedtuple
from typing import List, Dict

Label = namedtuple( 'Label' , [
    'name'        ,
    'id'          , 
    'category'    , 
    'categoryId'  , 
    'hasInstances',
    'ignoreInEval',
    'color'
    ] )


def get_labels(is_rugd: bool = True) -> List[Label]:
    # Color for concrete differs between RUGD and RELLIS-3D datasets
    concrete_color = (101, 101, 11) if is_rugd else (170, 170, 170)

    labels = [
        #       name                     id       category            catId     hasInstances   ignoreInEval        color
        Label(  'void'                 ,  0      , 'void'               , 0       , False        , True          , (  0,  0,  0) ),
        Label(  'dirt'                 ,  1      , 'drivable'           , 1       , False        , False         , (  108, 64, 20) ),
        Label(  'sand'                 ,  2      , 'drivable'           , 1       , False        , False         , (  255, 229, 204) ),
        Label(  'grass'                ,  3      , 'drivable'           , 1       , False        , False         , (  0, 102, 0) ),
        Label(  'tree'                 ,  4      , 'obstacle'           , 2       , False        , False         , (  0, 255, 0) ),
        Label(  'water'                ,  5      , 'obstacle'           , 2       , False        , False         , (  0, 128, 255) ),
        Label(  'sky'                  ,  6      , 'sky'                , 3       , False        , False         , (  0, 0, 255) ),
        Label(  'generic-object'       ,  7      , 'object'             , 5       , False        , False         , (  255, 0, 127) ),
        Label(  'asphalt'              ,  8      , 'drivable'           , 1       , False        , False         , (  64, 64, 64) ),
        Label(  'gravel'               ,  9      , 'drivable'           , 1       , False        , False         , (  255, 128, 0) ),
        Label(  'building'             ,  10     , 'construction'       , 6       , False        , False         , (  255, 0, 0) ),
        Label(  'mulch'                ,  11     , 'drivable'           , 1       , False        , False         , (  153, 76, 0) ),
        Label(  'rock-bed'             ,  12     , 'obstacle'           , 2       , False        , False         , (  102, 102, 0) ),
        Label(  'fence'                ,  13     , 'obstacle'           , 2       , False        , False         , (  102, 0, 204) ),
        Label(  'bush'                 ,  14     , 'obstacle'           , 2       , False        , False         , (  255, 153, 204) ),
        Label(  'sign'                 ,  15     , 'object'             , 5       , False        , False         , (  0, 102, 102) ),
        Label(  'rock'                 ,  16     , 'obstacle'           , 2       , False        , False         , (  153, 204, 255) ),
        Label(  'bridge'               ,  17     , 'construction'       , 6       , False        , False         , (  102, 255, 255) ),
        Label(  'concrete'             ,  18     , 'drivable'           , 1       , False        , False         , concrete_color ),
        Label(  'barrier'              ,  19     , 'obstacle'           , 2       , False        , False         , (  41, 121, 255) ),
        Label(  'mud'                  ,  20     , 'drivable'           , 1       , False        , False         , (  99, 66, 34) ),
        Label(  'rubble'               ,  21     , 'obstacle'           , 2       , True         , False         , (  110, 22, 138) ),
        Label(  'puddle'               ,  22     , 'obstacle'           , 2       , True         , False         , (  134, 255, 239) ),
        Label(  'picnic-table'         ,  23     , 'object'             , 5       , True         , False         , (  114, 85, 47) ),
        Label(  'log'                  ,  24     , 'obstacle'           , 2       , True         , False         , (  102, 0, 0) ),
        Label(  'bicycle'              ,  25     , 'vehicle'            , 4       , True         , False         , (  0, 255, 128) ),
        Label(  'person'               ,  26     , 'human'              , 7       , True         , False         , (  204, 153, 255) ),
        Label(  'vehicle'              ,  27     , 'vehicle'            , 4       , True         , False         , (  255, 255, 0) ),
        Label(  'pole'                 ,  28     , 'obstacle'           , 2       , True         , False         , (  0, 153, 153) ),
    ]

    return labels


def get_color2labels(is_rugd: bool = True) -> Dict[tuple, Label]:
    return { label.color: label for label in get_labels(is_rugd) }


def get_id2labels(is_rugd: bool = True) -> Dict[int, Label]:
    return { label.id: label for label in get_labels(is_rugd) }


def get_conflict_colormap() -> Dict[tuple, tuple]:
    conflict_colormap = {}
    for rugd_label, rellis_label in zip(get_labels(is_rugd=True), get_labels(is_rugd=False)):
        if rugd_label.color != rellis_label.color:
            conflict_colormap[rugd_label.color] = rellis_label.color

    return conflict_colormap
